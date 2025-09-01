import os
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError


class CourseStore:
    """
    End-to-end DynamoDB handler for 'Courses' data.

    - Normalizes raw scraper items (partners/subjects lists -> list + *_primary scalar)
    - Upsert single/batch
    - Insert-only (conditional put)
    - Get / BatchGet
    - Update (SET/REMOVE/ADD)
    - Delete (with optional condition)
    - Scan (paginated)
    - Query by GSIs (partner_primary / subject_primary)

    Table assumptions:
      PK: uuid (S)
      Optional GSIs:
        - PartnerIndex  (HASH: partner_primary)
        - SubjectIndex  (HASH: subject_primary)
    """

    def __init__(
        self,
        table_name: Optional[str] = None,
        region_name: Optional[str] = None,
        overwrite_batch: bool = True,
    ) -> None:
        self.table_name = table_name or os.getenv("DDB_TABLE", "Courses")
        self.region_name = region_name or os.getenv("AWS_REGION", "ap-southeast-2")
        self.overwrite_batch = overwrite_batch

        self.ddb = boto3.resource("dynamodb", region_name=self.region_name)
        self.table = self.ddb.Table(self.table_name)

    # ---------- Public: Normalization / Mapping ----------

    @staticmethod
    def _to_number(n: Any) -> Decimal:
        try:
            return Decimal(str(int(n)))
        except Exception:
            return Decimal("0")

    @staticmethod
    def _as_str_list(v: Any) -> List[str]:
        """Coerce partner/subject into a clean List[str]."""
        if v is None:
            return []
        if isinstance(v, list):
            out: List[str] = []
            for el in v:
                if isinstance(el, str):
                    s = el.strip()
                    if s:
                        out.append(s)
                elif isinstance(el, dict):
                    for k in ("name", "title", "partner", "provider", "display_name"):
                        val = el.get(k)
                        if isinstance(val, str) and val.strip():
                            out.append(val.strip())
                            break
            # de-dup preserve order
            seen = set()
            deduped = []
            for s in out:
                if s not in seen:
                    seen.add(s)
                    deduped.append(s)
            return deduped
        if isinstance(v, str):
            s = v.strip()
            return [s] if s else []
        if isinstance(v, (int, float, Decimal)):
            return [str(v)]
        return []

    @staticmethod
    def _primary(values: Sequence[str]) -> Optional[str]:
        return values[0] if values else None

    def map_raw_hit(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Map a raw edX hit to the DynamoDB item shape."""
        uuid = str(item.get("uuid", "")).strip()
        if not uuid:
            return None

        partners = self._as_str_list(item.get("partner"))
        subjects = self._as_str_list(item.get("subject"))

        mapped: Dict[str, Any] = {
            "uuid": uuid,  # PK
            "title": item.get("title"),
            "img_url": item.get("card_image_url"),
            "lang": item.get("language"),
            "learning_type": item.get("learning_type"),
            "level": item.get("level"),
            "primary_description": item.get("primary_description"),
            "secondary_description": item.get("secondary_description"),
            "url": item.get("marketing_url"),
            "enrol_cnt": self._to_number(item.get("recent_enrollment_count")),
            "partners": partners,  # full list
            "subjects": subjects,  # full list
        }

        partner_primary = self._primary(partners)
        subject_primary = self._primary(subjects)
        if partner_primary:
            mapped["partner_primary"] = partner_primary
            # If your existing GSI is on 'partner', also mirror:
            # mapped["partner"] = partner_primary
        if subject_primary:
            mapped["subject_primary"] = subject_primary
            # If your existing GSI is on 'subject', also mirror:
            # mapped["subject"] = subject_primary

        return mapped

    # ---------- Public: Write APIs ----------

    def put_upsert(self, item: Dict[str, Any]) -> None:
        """Upsert (PutItem) — last write wins."""
        self.table.put_item(Item=item)

    def put_insert_only(self, item: Dict[str, Any]) -> None:
        """Insert-only — fail if PK already exists."""
        self.table.put_item(
            Item=item, ConditionExpression="attribute_not_exists(uuid)"
        )

    def put_many(self, items: Iterable[Dict[str, Any]]) -> int:
        """
        Batch upsert many items (overwrite by PK if configured).
        Returns number of items attempted.
        """
        count = 0
        if self.overwrite_batch:
            with self.table.batch_writer(overwrite_by_pkeys=["uuid"]) as batch:
                for it in items:
                    batch.put_item(Item=it)
                    count += 1
        else:
            # batch_writer doesn't support conditional writes; fall back per item
            for it in items:
                self.put_insert_only(it)
                count += 1
        return count

    # ---------- Public: Read APIs ----------

    def get(self, uuid: str) -> Optional[Dict[str, Any]]:
        resp = self.table.get_item(Key={"uuid": uuid})
        return resp.get("Item")

    def batch_get(self, uuids: Sequence[str]) -> List[Dict[str, Any]]:
        """BatchGet up to 100 keys at a time (DynamoDB limit)."""
        client = self.ddb.meta.client
        keys = [{"uuid": u} for u in uuids]
        items: List[Dict[str, Any]] = []
        while keys:
            chunk, keys = keys[:100], keys[100:]
            resp = client.batch_get_item(
                RequestItems={self.table_name: {"Keys": chunk}}
            )
            items.extend(resp.get("Responses", {}).get(self.table_name, []))
            unprocessed = resp.get("UnprocessedKeys", {}).get(self.table_name, {})
            keys.extend(unprocessed.get("Keys", []))
        return items

    # ---------- Public: Query (GSIs) ----------

    def query_by_partner(self, partner_primary: str, **kwargs) -> List[Dict[str, Any]]:
        """Query GSI PartnerIndex on partner_primary."""
        resp = self.table.query(
            IndexName="PartnerIndex",
            KeyConditionExpression="partner_primary = :p",
            ExpressionAttributeValues={":p": partner_primary},
            **kwargs,
        )
        return resp.get("Items", [])

    def query_by_subject(self, subject_primary: str, **kwargs) -> List[Dict[str, Any]]:
        """Query GSI SubjectIndex on subject_primary."""
        resp = self.table.query(
            IndexName="SubjectIndex",
            KeyConditionExpression="subject_primary = :s",
            ExpressionAttributeValues={":s": subject_primary},
            **kwargs,
        )
        return resp.get("Items", [])

    # ---------- Public: Update / Delete ----------

    def update(
        self,
        uuid: str,
        set_attrs: Optional[Dict[str, Any]] = None,
        remove_attrs: Optional[Sequence[str]] = None,
        add_numbers: Optional[Dict[str, int]] = None,
        condition: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Flexible UpdateItem builder.

        - set_attrs: dict of attribute -> new value
        - remove_attrs: list of attribute names to remove
        - add_numbers: dict of number-attr -> amount to ADD (increment)
        - condition: optional ConditionExpression (string)

        Returns the updated item.
        """
        updates: List[str] = []
        names: Dict[str, str] = {}
        values: Dict[str, Any] = {}

        def n(alias: str) -> str:
            names[f"#{alias}"] = alias
            return f"#{alias}"

        def v(alias: str, val: Any) -> str:
            # Coerce ints to Decimal for Number attributes if needed
            if isinstance(val, int):
                val = Decimal(str(val))
            values[f":{alias}"] = val
            return f":{alias}"

        if set_attrs:
            sets = []
            for k, val in set_attrs.items():
                sets.append(f"{n(k)} = {v(k, val)}")
            if sets:
                updates.append("SET " + ", ".join(sets))

        if remove_attrs:
            removes = [n(k) for k in remove_attrs]
            if removes:
                updates.append("REMOVE " + ", ".join(removes))

        if add_numbers:
            adds = []
            for k, amt in add_numbers.items():
                adds.append(f"{n(k)} {v(k, Decimal(str(amt)))}")
            if adds:
                updates.append("ADD " + ", ".join(adds))

        update_expr = " ".join(updates) if updates else "SET #_noop = :zero"
        if not updates:
            names["#_noop"] = "_noop"
            values[":zero"] = Decimal("0")

        kwargs: Dict[str, Any] = dict(
            Key={"uuid": uuid},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=names or None,
            ExpressionAttributeValues=values or None,
            ReturnValues="ALL_NEW",
        )
        if condition:
            kwargs["ConditionExpression"] = condition

        resp = self.table.update_item(**{k: v for k, v in kwargs.items() if v is not None})
        return resp.get("Attributes", {})

    def delete(self, uuid: str, condition: Optional[str] = None) -> None:
        kwargs: Dict[str, Any] = {"Key": {"uuid": uuid}}
        if condition:
            kwargs["ConditionExpression"] = condition
        self.table.delete_item(**kwargs)

    # ---------- Public: Scans ----------

    def scan_all(self, projection: Optional[str] = None, page_limit: int = 1000):
        items = []
        kwargs = {"Limit": page_limit}

        if projection:
            # Handle reserved keywords by aliasing them automatically
            names = {}
            expr_parts = []
            for attr in [p.strip() for p in projection.split(",")]:
                alias = "#" + attr
                names[alias] = attr
                expr_parts.append(alias)
            kwargs["ProjectionExpression"] = ", ".join(expr_parts)
            kwargs["ExpressionAttributeNames"] = names

        while True:
            resp = self.table.scan(**kwargs)
            items.extend(resp.get("Items", []))
            if "LastEvaluatedKey" not in resp:
                break
            kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]

        return items

    # ---------- Pipeline helpers ----------

    def save_raw_hits(self, raw_hits: Iterable[Dict[str, Any]]) -> int:
        """Map raw scraper hits then batch write."""
        mapped: List[Dict[str, Any]] = []
        for raw in raw_hits:
            m = self.map_raw_hit(raw)
            if m:
                mapped.append(m)
        return self.put_many(mapped)


