# Speedy Changelog

All notable changes to this project will be documented in this file. 

## - 25-02-2023

### Added
- Support for cancelling a speed test
- `set_cancelled()` method to `SpeedyFrame` to set the test cancellation state
- `is_cancelled()` method to `SpeedyFrame` to check the test cancellation state
- `on_cancel()` method to `SpeedyFrame` to handle cancelling a speed test
- `show_cancel_button()` method to `SpeedyFrame` to show the cancel button
- `hide_cancel_button()` method to `SpeedyFrame` to hide the cancel button
- `set_focus_to_cancel_button()` method to `SpeedyFrame` to set the focus to the cancel button
- `set_cancel_button_label()` method to `SpeedyFrame` to set the label of the cancel button

### Changed
- Refactored `SpeedyFrame` class to remove duplicate method definitions

## - 24-02-2023
Initial release of Speedy app code.
