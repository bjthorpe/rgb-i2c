
'''
def manager_display_live():
    global bus
    global displays
    global g_break
    global g_update_displays

    time_last_error_msg = time()

    while True:
        start_time = time()

        if g_update_displays:
            for display in displays.values():
                if display.needs_updating:
                    display.display_current_frame(bus)
                    display.needs_updating = False

            g_update_displays = False

        end_time = time()

        sleep_time = FRAME_RATE - (end_time - start_time)

        if sleep_time < 0.001:
            if (time() - time_last_error_msg) > 1.0:
                print('Warning: time to display frames taking longer than the frame rate.')
                time_last_error_msg = time()
        else:
            sleep(sleep_time)

        if g_break:
            break
'''


'''
def manager_data_live():
    global bus
    global displays
    global g_break
    global g_update_displays

    test_pixel_updated = False  # TODO: remove after testing.
    test_timer = 5.0  # TODO: remove after testing.

    change_detected = False  # Flag for recording if there are any change in pixels of a display.

    time_last_change_check = time()
    time_last_error_msg = -999.0

    t1 = time()

    while True:
        start_time = time()

        change_detected = False

        # If a new data detection point comes in, apply it.
        # START OF TESTS -> TODO: remove after testing.
        for display in displays.values():
            # TEST 1: Update a pixel with a gradient after a few seconds ->
            if test_timer < 4.0 and not test_pixel_updated:
                display.update_pixel_gradient(2, 5, gradient=range(0, 50, 10))
                test_pixel_updated = True
    
            # TEST 2: random frames ->
            #random_frame = create_pixels([randint(0, 255) for _ in range(size * size)])
            #display.update_frame(random_frame)
        # END OF TESTS ->

        # Check for any change in pixels of the displays.
        tick = time() - time_last_change_check

        for display in displays.values():
            display.check_pixel_changes(tick)

            change_detected = change_detected or display.change_detected

        time_last_change_check = time()

        # Apply changes to background frame if any have been detected.
        for display in displays.values():
            display.apply_pixel_changes()

        # Pixels updated, so switch the buffer if a chance has been detected.
        for display in displays.values():
            if display.change_detected:
                display.switch_buffer()
                display.needs_updating = True

        if change_detected:
            g_update_displays = True  # Tells the display thread to update the display as we've had a change.

        # Copy the displayed frame to the buffered frame if a change was detected.
        for display in displays.values():
            if display.change_detected:
                display.copy_buffer()

        for display in displays.values():
            display.change_detected = False

        end_time = time()

        sleep_time = FRAME_RATE - (end_time - start_time)

        if sleep_time < 0.001:
            if (time() - time_last_error_msg) > 1.0:
                print('Warning: time to copy data between buffers and pixel updates is taking longer than the frame rate.')
                time_last_error_msg = time()
        else:
            sleep(sleep_time)

        # TODO: remove after testing.
        test_timer -= FRAME_RATE

        # TODO: remove after testing.
        if test_timer < 0.0:
            g_break = True

        if g_break:
            break

    t2 = time()

    print('Time taken', t2-t1)
'''


'''
class Display:
    def update_pixel_gradient(self, x, y, gradient, timers=None):
        assert isinstance(x, int)
        assert isinstance(y, int)

        assert x < self.size, 'Pixel requested out of x bounds.'
        assert y < self.size, 'Pixel requested out of y bounds.'

        if self.display_frame_A:
            self.frame_B[x + 8 * y].set_gradient(gradient, timers)
        else:
            self.frame_A[x + 8 * y].set_gradient(gradient, timers)

        self.change_detected = True

    def update_frame(self, frame):
        assert all(isinstance(i, Pixel) for i in frame)

        assert len(frame) == self.size * self.size

        if self.display_frame_A:
            self.frame_B = frame
        else:
            self.frame_A = frame

        self.change_detected = True

    def check_pixel_changes(self, tick):
        assert isinstance(tick, (float, int))

        assert tick > 0.0, 'Tick should be > 0.0.'

        for pixel in self.frame_A if not self.display_frame_A else self.frame_B:
            pixel.check_change(tick)

        self.change_detected = self.change_detected or \
            any(pixel.change_detected for pixel in (self.frame_A if not self.display_frame_A else self.frame_B))

    def apply_pixel_changes(self):
        for pixel in self.frame_A if not self.display_frame_A else self.frame_B:
            pixel.apply_change()
'''

