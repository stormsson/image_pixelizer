# Feature Specification: Photographic Editing Tools

**Feature Branch**: `004-photo-editing-tools`  
**Created**: 2025-01-29  
**Status**: Draft  
**Input**: User description: "we want to add some photographic editing tools widgets accessible from the main menu and with new windows. first tool will be image levels. it shows a histogram with the frequencies of the different tones of pixels in the image showing dark tones on the left and right tones on the right. it shows 2 sliders whose value goes from 0 to 100. they will be lights_cutoff and darks_cutoff. changing the lights_cutoff slider value will replace the lighter [slider_value]% with the next available color. changing the darks_cutoff slider value will replace the darker [slider_value]% with the next available color"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Image Levels Tool (Priority: P1) 🎯 MVP

A user has loaded an image and wants to adjust the tonal distribution using levels adjustment. They access the "Image Levels" option from the main menu, which opens a new window displaying a histogram of the image's tonal distribution. The histogram shows dark tones on the left and light tones on the right, with vertical bars representing the frequency of pixels at each tone level. The window contains two sliders: "Lights Cutoff" and "Darks Cutoff", each ranging from 0 to 100. As the user adjusts the Lights Cutoff slider, the lighter percentage of pixels (corresponding to the slider value) are replaced with the brightest available color (white/255). Similarly, adjusting the Darks Cutoff slider replaces the darker percentage of pixels with the darkest available color (black/0). The histogram updates in real-time to reflect the changes, and the main image view updates to show the adjusted result.

**Why this priority**: Image levels adjustment is a fundamental photographic editing tool that allows users to improve contrast and tonal distribution. This is the first tool in a suite of editing tools, establishing the pattern for menu access and window-based tool interfaces.

**Independent Test**: Can be fully tested by loading an image, accessing "Image Levels" from the main menu, verifying the histogram displays correctly, adjusting both sliders, and confirming that the image updates to show the levels adjustment applied. The tool should work independently of other editing operations.

**Acceptance Scenarios**:

1. **Given** an image is loaded, **When** a user selects "Image Levels" from the main menu, **Then** a new window opens displaying a histogram of the image's tonal distribution, calculated from a snapshot of the image state at the moment the window opened
2. **Given** the Image Levels window is open, **When** a user views the histogram, **Then** dark tones are displayed on the left side and light tones are displayed on the right side, with vertical bars showing pixel frequency at each tone level. The horizontal axis represents actual color values (0-255 for 8-bit images), not normalized values
3. **Given** the Image Levels window is open, **When** a user views the controls, **Then** two sliders are visible: "Lights Cutoff" and "Darks Cutoff", each with a range from 0 to 100
4. **Given** the Image Levels window is open with Lights Cutoff at 0, **When** a user moves the Lights Cutoff slider to a value N (0-100), **Then** the lightest N% of pixels (calculated from the image snapshot captured when the window opened) are replaced with the brightest available color (255/white)
5. **Given** the Image Levels window is open with Darks Cutoff at 0, **When** a user moves the Darks Cutoff slider to a value N (0-100), **Then** the darkest N% of pixels (calculated from the image snapshot captured when the window opened) are replaced with the darkest available color (0/black)
6. **Given** the Image Levels window is open, **When** a user adjusts either slider, **Then** the histogram updates in real-time to reflect the tonal changes
7. **Given** the Image Levels window is open, **When** a user adjusts either slider, **Then** the main image view updates in real-time to show the adjusted result
8. **Given** no image is loaded, **When** a user attempts to access "Image Levels" from the main menu, **Then** the menu option is disabled or an appropriate message is displayed
9. **Given** the Image Levels window is open, **When** a user closes the window, **Then** the levels adjustments remain applied to the image in the main view
10. **Given** an image has levels adjustments applied, **When** a user views the operation history, **Then** the levels adjustment is tracked as a separate operation that can be undone

---

### Edge Cases

- What happens when a user adjusts both sliders simultaneously? Both adjustments should apply correctly, with darks cutoff affecting the darkest pixels and lights cutoff affecting the lightest pixels, potentially creating a more contrasty image
- How does the system handle images that are already very dark or very light? The sliders should still function, potentially clipping more pixels to black or white respectively
- What happens when both sliders are set to 100? All pixels should be replaced with either black (darks) or white (lights), resulting in a binary image
- How does the system handle grayscale vs color images? The levels adjustment should work on the luminance/channel values, preserving color relationships for color images
- What happens when a user opens multiple editing tool windows? Each tool should open in its own window, and multiple tools can be open simultaneously
- How does the system handle very large images? The histogram calculation and slider adjustments should complete within reasonable time without freezing the UI
- What happens when a user adjusts sliders rapidly? The system should handle rapid slider movements smoothly, updating the display without lag or skipped updates
- How does undo interact with levels adjustments? Levels adjustments should be tracked in the operation history and can be undone independently of other operations. The snapshot captured when the window opens ensures undo can restore to the exact state before levels adjustment was applied

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a "Photographic Editing Tools" menu section in the main menu with submenu items for individual editing tools
- **FR-002**: System MUST provide an "Image Levels" menu item accessible from the main menu
- **FR-003**: System MUST open Image Levels tool in a new separate window when selected from the menu
- **FR-004**: System MUST display a histogram showing tonal distribution of the image snapshot captured when the window opened, with dark tones on the left and light tones on the right. The horizontal axis MUST represent actual color values (0-255 for 8-bit images), not normalized values
- **FR-005**: System MUST display vertical bars in the histogram representing pixel frequency at each tone level. Each bar position corresponds to a specific color value (0-255) on the horizontal axis
- **FR-006**: System MUST provide a "Lights Cutoff" slider with a range from 0 to 100
- **FR-007**: System MUST provide a "Darks Cutoff" slider with a range from 0 to 100
- **FR-008**: System MUST replace the lightest N% of pixels with the brightest available color (255/white) when Lights Cutoff slider is set to value N
- **FR-009**: System MUST replace the darkest N% of pixels with the darkest available color (0/black) when Darks Cutoff slider is set to value N
- **FR-010**: System MUST update the histogram in real-time as slider values change
- **FR-011**: System MUST update the main image view in real-time as slider values change
- **FR-012**: System MUST disable or prevent access to Image Levels tool when no image is loaded
- **FR-013**: System MUST allow multiple editing tool windows to be open simultaneously
- **FR-014**: System MUST track levels adjustments in the operation history as a separate undoable operation
- **FR-015**: System MUST capture a snapshot of the image state when the Image Levels window opens, and apply all cutoff calculations against this snapshot (not the live current state), ensuring reversibility and consistency
- **FR-016**: System MUST handle both grayscale and color images correctly, applying levels to appropriate channels

### Key Entities *(include if feature involves data)*

- **Editing Tool Window**: Represents a separate window for a photographic editing tool. Key attributes include: tool type (e.g., Image Levels), current slider values, histogram data, and a snapshot of the image state captured when the window opened. The snapshot is used as the base for all cutoff calculations to ensure reversibility and consistency. Used to provide isolated editing interfaces that don't interfere with the main application window.

- **Histogram Data**: Represents the tonal distribution of an image. Key attributes include: tone level (0-255 for 8-bit images), pixel frequency count at each tone level, and visual representation (bars). The horizontal axis represents actual color values (0-255 for 8-bit images), not normalized values. Used to visualize the distribution of dark, mid, and light tones in the image.

- **Levels Adjustment Parameters**: Represents the current state of levels adjustment. Key attributes include: lights_cutoff value (0-100), darks_cutoff value (0-100), and the resulting pixel mapping. Used to track and apply the levels transformation to the image.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can access Image Levels tool from the main menu and open the tool window within 1 second of clicking the menu item
- **SC-002**: Histogram displays correctly for images up to 2000x2000px, calculating and rendering within 2 seconds
- **SC-003**: Slider adjustments update the image display in real-time with no perceptible delay (under 100ms for typical images)
- **SC-004**: Users can adjust both sliders independently and see combined effects applied correctly in 100% of cases
- **SC-005**: Levels adjustments are applied correctly, with the specified percentage of pixels replaced as expected (verified by pixel analysis)
- **SC-006**: Multiple editing tool windows can be open simultaneously without performance degradation or UI conflicts
- **SC-007**: 95% of users can successfully apply levels adjustments on their first attempt without requiring instructions
- **SC-008**: Levels adjustments integrate correctly with existing undo/redo functionality, allowing users to revert changes independently

## Clarifications

### Session 2025-01-29

- Q: When the Image Levels window opens, should cutoff calculations be based on a snapshot of the image state at window open, or the live current state? → A: Snapshot at window open - capture image state when window opens, all cutoffs calculated against this snapshot for reversibility and consistency
- Q: What should the histogram horizontal axis domain represent? → A: The histogram horizontal axis domain should represent the available color values (0-255 for 8-bit images), not normalized values. The axis is not normalized.

## Assumptions

- "Next available color" for lights cutoff means the brightest color value (255 for 8-bit images, white)
- "Next available color" for darks cutoff means the darkest color value (0 for 8-bit images, black)
- Histogram updates in real-time as sliders are adjusted (no separate Apply button needed)
- Main image view updates in real-time to show preview of adjustments
- Levels adjustment works on luminance/channel values, preserving color relationships for color images
- Multiple editing tool windows can be open simultaneously
- Levels adjustments are tracked in operation history and can be undone
- When the Image Levels window opens, the system captures a snapshot of the current image state (including any previous modifications). All cutoff calculations are performed against this snapshot, not the live current state, ensuring the adjustment can be reversed via undo
- Slider values represent percentages of pixels to be affected (0% = no change, 100% = all pixels affected)
