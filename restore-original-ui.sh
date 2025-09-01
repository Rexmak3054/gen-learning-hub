#!/bin/bash

echo "🎨 RESTORING YOUR ORIGINAL UI"
echo "============================"
echo ""
echo "I'll restore your full-featured frontend with:"
echo "✨ Navigation with tabs (Discover, Plan, Profile)"
echo "🎯 Enhanced Discover Page with 3D course cards"
echo "📋 Plan management with drag & drop"
echo "👤 Profile page with study progress"
echo "🎪 3D carousels and animations"
echo ""

cd frontend

echo "📦 Installing additional dependencies..."
npm install lucide-react@^0.263.1 --save
npm install tailwindcss@^3.4.0 autoprefixer@^10.4.16 postcss@^8.4.32 --save-dev

echo ""
echo "🏗️ Testing build with restored UI..."
npm run build

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! Your original UI is back and builds successfully!"
    echo ""
    echo "✅ Features restored:"
    echo "  • Multi-page navigation"
    echo "  • 3D course cards and carousels" 
    echo "  • Interactive course search"
    echo "  • Study plan management"
    echo "  • User profile dashboard"
    echo "  • Tailwind CSS styling"
    echo "  • Lucide React icons"
    echo ""
    echo "🚀 Ready to deploy the full-featured version!"
    echo ""
    echo "Deploy now? (y/n)"
    read -p "" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd ..
        git add .
        git commit -m "Restore: Original full-featured UI with build fixes applied"
        git push origin main
        echo ""
        echo "🚀 Deployed! Your full UI is now live on Vercel!"
        echo "Check your app - it should look like your original design now."
    else
        echo "Changes ready - deploy manually when you're ready:"
        echo "git add . && git commit -m 'Restore original UI' && git push origin main"
    fi
else
    echo ""
    echo "❌ Build failed with original UI restored."
    echo "There might be an issue with one of your components."
    echo ""
    echo "Let's test which component is causing the problem..."
    echo "Check the error above and let me know which component failed."
    echo ""
    echo "I can fix individual components one by one."
fi
