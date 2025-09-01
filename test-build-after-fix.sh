#!/bin/bash

echo "🧪 TESTING IF AJV FIX WORKED"
echo "============================"
echo ""

cd frontend

echo "🏗️ Testing build process..."
npm run build

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! AJV error fixed!"
    echo "✅ Frontend builds successfully"
    echo ""
    echo "📊 Build details:"
    echo "Build folder size: $(du -sh build/ 2>/dev/null | cut -f1)"
    echo "Build files created: $(find build -type f | wc -l) files"
    echo ""
    echo "🚀 READY TO DEPLOY TO VERCEL!"
    echo ""
    echo "Next steps:"
    echo "1. git add ."
    echo "2. git commit -m 'Fix: Resolve AJV dependency conflict'"
    echo "3. git push origin main"
    echo "4. Vercel will auto-redeploy successfully!"
    echo ""
    echo "Would you like me to commit and push now? (y/n)"
    read -p "" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd ..
        git add .
        git commit -m "Fix: Resolve AJV dependency conflict - frontend builds successfully"
        git push origin main
        echo ""
        echo "🚀 Pushed to GitHub! Vercel will redeploy automatically."
        echo "Check your Vercel dashboard for deployment progress."
        echo ""
        echo "Test your app after deployment:"
        echo "• Frontend: https://your-app.vercel.app"
        echo "• API: https://your-app.vercel.app/api/health"
    else
        echo "Manual deployment - run these commands when ready:"
        echo "git add . && git commit -m 'Fix: AJV error resolved' && git push origin main"
    fi
else
    echo ""
    echo "❌ Build still failing..."
    echo "Let's try the nuclear option:"
    echo ""
    echo "Run: ./nuclear-fix.sh"
    echo "Or try: ./fix-ajv-complete.sh for automated multi-step fix"
    echo ""
    echo "Build error details above ☝️"
fi
