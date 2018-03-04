# PiLock Release Changelog

## V0.3.1:
- More fixes. What a surprise!
- Major rework on the internals. Refactored almost all of the codebase.
- Converted PiLock to a Python3 Project.
- PiLock now uses venv (should've done that ages ago...).
- Added tests and CI Integration.
- Added Pagination to the Access Log.

## V0.3.0:
- Fixes. LOTS OF THEM!
- Added PINless unlocks. You no longer need to type your PIN every time you unlock, should you so desire.
- Created an Android Wear app/module. You can now unlock using your wearable! 
- AuthTokens, WearTokens and PINs now get hashed.
- AuthToken gets encrypted while on the mobile device.
- Created a notification system. Notifies when server software updates are available and if the Debug Mode is enabled.
- Added Unlock functionality from within the AdminCP.
- The server can now be made public. Unlocks can be performed via mobile data.
