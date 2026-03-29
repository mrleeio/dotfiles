#!/bin/bash
# Switches Terminal.app profile based on macOS system appearance.
# Triggered by LaunchAgent when system appearance changes.

DARK_PROFILE="catppuccin-mocha"
LIGHT_PROFILE="catppuccin-latte"

MODE=$(defaults read -g AppleInterfaceStyle 2>/dev/null || echo "Light")

if [ "$MODE" = "Dark" ]; then
  PROFILE="$DARK_PROFILE"
else
  PROFILE="$LIGHT_PROFILE"
fi

defaults write com.apple.Terminal "Default Window Settings" -string "$PROFILE"
defaults write com.apple.Terminal "Startup Window Settings" -string "$PROFILE"

osascript -e "
if application \"Terminal\" is running then
  tell application \"Terminal\"
    set target to settings set \"$PROFILE\"
    set default settings to target
    repeat with w in every window
      repeat with t in every tab of w
        set current settings of t to target
      end repeat
    end repeat
  end tell
end if
" 2>/dev/null
