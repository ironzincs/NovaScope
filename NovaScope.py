import tkinter as tk
from tkinter import ttk, messagebox
import requests
from tkintermapview import TkinterMapView
from tkcalendar import Calendar
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from timezonefinder import TimezoneFinder
from datetime import datetime
import math
import pytz
import random
from PIL import Image, ImageTk
from geopy.geocoders import Nominatim


class StarObservationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NovaSpace")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        # Load and display NovaSpace logo
        # Set the application icon
        try:
            self.icon = Image.open("Icon.ico")  # Replace with your logo filename
            self.icon_img = ImageTk.PhotoImage(self.icon)
            self.root.iconphoto(False, self.icon_img)
        except FileNotFoundError:
            print("NovaSpace")
        self.user_location = self.get_user_location()
        # Apply a modern theme
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Modern theme
        self.style.configure("TButton", font=("Helvetica", 10), padding=6)
        self.style.configure("TLabel", font=("Helvetica", 11), padding=4)
        self.root.configure(bg="#E3F2FD")  # Light blue
        self.style.configure("TLabel", background="#E3F2FD", foreground="black")
        self.style.configure("TButton", background="#BBDEFB", foreground="black")

        self.light_mode_colors = {"background": "#E3F2FD", "button": "#007BFF", "text": "#000000"}

        self.current_colors = self.light_mode_colors  # Start with light mode

        # Add a dark mode toggle
        self.dark_mode = tk.BooleanVar(value=False)
        self.create_menu_bar()


        # Footer
        self.create_footer()
        # Initialize variables
        self.clicked_lat = None
        self.clicked_lon = None
        self.current_marker = None

        # Create GUI components
        self.create_widgets()
    def create_menu_bar(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Reset", command=self.reset_inputs, accelerator="Ctrl+R")
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        menu_bar.add_cascade(label="File", menu=file_menu)

        # View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_checkbutton(label="Dark Mode", variable=self.dark_mode, command=self.toggle_dark_mode)
        menu_bar.add_cascade(label="View", menu=view_menu)

        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        # Keyboard shortcuts
        self.root.bind("<Control-r>", lambda event: self.reset_inputs())
        self.root.bind("<Control-q>", lambda event: self.root.quit())

    def get_user_location(self):
        """Fetch user location using a geolocation API."""
        try:
            response = requests.get("http://ip-api.com/json/")
            data = response.json()
            return (data["lat"], data["lon"])  # Latitude and Longitude
        except Exception as e:
            print("Could not determine user location:", e)
            return (0, 0)  # Fallback to (0, 0) if location is unavailable

    def toggle_dark_mode(self):
        """Toggle dark mode on and off."""
        if self.dark_mode.get():
            # Dark blue background
            self.root.configure(bg="#1A237E")  # Dark blue
            self.style.configure("TLabel", background="#1A237E", foreground="#ECF0F1")
            self.style.configure("TButton", background="#3949AB", foreground="#ECF0F1")
            self.dark_mode_colors = {"background": "#BBDEFB", "button": "#3949AB", "text": "#FFFFFF"}
            self.current_colors = self.dark_mode_colors
        else:
            # Light blue background
            self.root.configure(bg="#E3F2FD")  # Light blue
            self.style.configure("TLabel", background="#E3F2FD", foreground="black")
            self.style.configure("TButton", background="#BBDEFB", foreground="black")
            self.light_mode_colors = {"background": "#E3F2FD", "button": "#007BFF", "text": "#000000"}
            self.current_colors = self.light_mode_colors



    def create_footer(self):
        footer = tk.Frame(self.root, bg="#34495E", height=30)
        footer.pack(side=tk.BOTTOM, fill=tk.X)

        credit_text = ("Lecturer: Prof. Dr. rer. nat. Abdurrouf S.Si. M.Si. | "
                       "Developed by: Muhammad Imron Rosyady | "
                       "Email: arklinatc21@gmail.com | Instagram: @mronnz")
        ttk.Label(footer, text=credit_text, background="lightgray", foreground="black", font=("Helvetica", 9)).pack()

    def create_widgets(self):
        """Create and arrange GUI widgets."""
        # Observation mode options
        self.types = ["Single Star", "Multiple Stars"]
        self.options = tk.StringVar(value=self.types[0])  # Default to "Single Star"

        # Observation mode selection
        ttk.Label(self.root, text="Observation Mode:", background=self.current_colors['background'], foreground='black').pack(pady=5)
        self.option_menu = ttk.OptionMenu(self.root, self.options, 'Single Star',
                                          *self.types, command=self.update_mode)
        self.option_menu.pack()

        # Frame for dynamic input fields
        self.dynamic_frame = ttk.Frame(self.root)
        self.dynamic_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Frame for action buttons
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=10)

        ttk.Button(self.button_frame, text="Calculate Observation", command=self.calculate_observation).pack(
            side=tk.LEFT, padx=10
        )
        ttk.Button(self.button_frame, text="Reset", command=self.reset_inputs).pack(side=tk.LEFT, padx=10)
        ttk.Button(self.button_frame, text="About", command=self.show_about).pack(side=tk.LEFT, padx=10)

        # Label for displaying results
        self.result_label = ttk.Label(self.root, text="", foreground="blue", wraplength=600, justify="left")
        self.result_label.pack(pady=10)

        # Initialize the default mode
        self.update_mode(self.types[0])

    def update_mode(self, mode):
        """Update input form based on the selected mode."""
        # Clear the dynamic frame
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()
        # Recreate the option menu to ensure it retains all options
        # Create appropriate input fields
        if mode == "Single Star":
            self.create_single_star_inputs()
        elif mode == "Multiple Stars":
            self.create_multiple_stars_inputs()

    def show_about(self):
        """Display an enhanced About dialog with logo and detailed information."""
        about_window = tk.Toplevel(self.root)
        about_window.title("About NovaSpace")
        about_window.geometry("600x500")
        about_window.resizable(False, False)

        # UB Logo
        try:
            ub_logo = Image.open("ub_logo.png")  # Replace with your UB logo file
            ub_logo_img = ImageTk.PhotoImage(ub_logo)
            logo_label = ttk.Label(about_window, image=ub_logo_img)
            logo_label.image = ub_logo_img  # Keep reference to avoid garbage collection
            logo_label.pack(pady=10)
        except FileNotFoundError:
            tk.Label(about_window, text="Brawijaya University", font=("Arial", 14, "bold")).pack(pady=10)

        # About Text
        about_text = (
            "This program aims to calculate the observability of stars based on a predetermined time and location.\n\n"
            "\nThe input data required in this program are:\n"
            "- Observer location (latitude and longitude)\n"
            "- Date and time\n"
            "- Star name (Right ascension and declination)\n\n"
            "This program was created by: Muhammad Imron Rosyady\n"
            "Advisor: Prof. Dr. rer. nat. Abdurrouf S.Si. M.Si.\n\n"
        )
        ttk.Label(about_window, text=about_text, wraplength=550, justify=tk.LEFT, font=("Arial", 10)).pack(pady=5)

        # Clickable Links
        links_frame = ttk.Frame(about_window)
        links_frame.pack(pady=10)
        # Close Button
        ttk.Button(about_window, text="Close", command=about_window.destroy).pack(pady=10)

        def open_link(url):
            import webbrowser
            webbrowser.open(url)

        links = [
            ("E-mail", "mailto:arklinatc21@gmail.com"),
            ("Instagram", "https://www.instagram.com/mronnz/profilecard/?igsh=MTJmb243bTdlajhpbg=="),
            ("LinkedIn",
             "https://www.linkedin.com/in/muhammad-imron-rosyady-119462267?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app"),
            ("GitHub", "https://github.com/ironzincs"),
        ]
        tk.Label(links_frame, text="My Social Media").pack()
        for name, urls in links:
            tk.Label(links_frame, text=name, fg="blue", cursor="hand2", font=("Arial", 10, "underline")).pack()
            tk.Label(links_frame, text=f"{urls}", fg="blue", cursor="hand2", font=("Arial", 8), anchor="w").bind(
                "<Button-1>", lambda e, url=urls: open_link(url))

        # Close Button
        tk.Button(about_window, text="Close", command=about_window.destroy).pack(pady=10)

    def create_single_star_inputs(self):
        """Create input form for single star observation."""
        self.input_common()

        tk.Label(self.dynamic_frame, text="Star Name:").grid(row=1, column=0, padx=5, pady=5)
        self.star_entry = tk.Entry(self.dynamic_frame, fg='gray')
        self.star_entry.grid(row=1, column=1, padx=5, pady=5)
        self.star_entry.insert(0, "Enter star name...")
        self.star_entry.bind('<FocusIn>', lambda event: self.clear_placeholder(self.star_entry, "Enter star name..."))
        self.star_entry.bind('<FocusOut>', lambda event: self.set_placeholder(self.star_entry, "Enter star name..."))

        tk.Button(self.dynamic_frame, text="Random Star", command=self.select_random_star).grid(row=1, column=2, padx=5,
                                                                                                pady=5)

    def create_multiple_stars_inputs(self):
        """Create input form for multiple stars observation."""
        self.input_common()
        self.obs_only = tk.IntVar()
        tk.Checkbutton(self.dynamic_frame, text="Observable Only", variable=self.obs_only).grid(row=1, column=2, padx=5,
                                                                                                pady=5)
        tk.Label(self.dynamic_frame, text="Number of Stars:").grid(row=1, column=0, padx=5, pady=5)
        self.num_stars_entry = tk.Entry(self.dynamic_frame, fg='gray')
        self.num_stars_entry.grid(row=1, column=1, padx=5, pady=5)
        self.num_stars_entry.insert(0, "Enter number of stars...")
        self.num_stars_entry.bind('<FocusIn>', lambda event: self.clear_placeholder(self.num_stars_entry,
                                                                                    "Enter number of stars..."))
        self.num_stars_entry.bind('<FocusOut>',
                                  lambda event: self.set_placeholder(self.num_stars_entry, "Enter number of stars..."))

    def input_common(self):
        tk.Label(self.dynamic_frame, text='Location:').grid(row=0, column=0, padx=5, pady=5)
        self.lat_entry = tk.Entry(self.dynamic_frame, fg='gray')
        self.lat_entry.grid(row=0, column=1, padx=5, pady=5)
        self.lon_entry = tk.Entry(self.dynamic_frame, fg='gray')
        self.lon_entry.grid(row=0, column=2, padx=3, pady=3)
        self.lon_entry.insert(0, "Longitude")
        self.lon_entry.bind('<FocusIn>', lambda event: self.clear_placeholder(self.lon_entry,
                                                                                    "Longitude"))
        self.lon_entry.bind('<FocusOut>',
                                  lambda event: self.set_placeholder(self.lon_entry, "Longitude"))
        self.lat_entry.insert(0, "Latitude")
        self.lat_entry.bind('<FocusIn>', lambda event: self.clear_placeholder(self.lat_entry,
                                                                              "Latitude"))
        self.lat_entry.bind('<FocusOut>',
                            lambda event: self.set_placeholder(self.lat_entry, "Latitude"))
        tk.Label(self.dynamic_frame, text="Date:").grid(row=2, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(self.dynamic_frame , fg='gray')
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)
        self.date_entry.insert(0, "YYYY-MM-DD")
        self.date_entry.bind('<FocusIn>', lambda event: self.clear_placeholder(self.date_entry,
                                                                              "YYYY-MM-DD"))
        self.date_entry.bind('<FocusOut>',
                            lambda event: self.set_placeholder(self.date_entry, "YYYY-MM-DD"))
        tk.Label(self.dynamic_frame, text="Date:").grid(row=2, column=0, padx=5, pady=5)

        tk.Button(self.dynamic_frame, text="Select Date", command=self.calendar_call).grid(row=2, column=2,
                                                                                           padx=5,
                                                                                           pady=5)

        tk.Label(self.dynamic_frame, text="Time:").grid(row=3, column=0, pady=5)

        time_frame = tk.Frame(self.dynamic_frame)
        time_frame.grid(row=3, column=1, pady=5)

        self.hours = ttk.Combobox(time_frame, values=[f"{i:02d}" for i in range(24)], width=2)
        self.hours.current(0)
        self.hours.pack(side=tk.LEFT)

        tk.Label(time_frame, text=":").pack(side=tk.LEFT)

        self.minutes = ttk.Combobox(time_frame, values=[f"{i:02d}" for i in range(60)], width=2)
        self.minutes.current(0)
        self.minutes.pack(side=tk.LEFT)

        tk.Label(time_frame, text=":").pack(side=tk.LEFT)

        self.seconds = ttk.Combobox(time_frame, values=[f"{i:02d}" for i in range(60)], width=2)
        self.seconds.current(0)
        self.seconds.pack(side=tk.LEFT)

        # Button to set the current time
        tk.Button(self.dynamic_frame, text="Current Time", command=self.set_current_time).grid(row=3, column=2,
                                                                                                   padx=5, pady=5)

        tk.Button(self.dynamic_frame, text="Open Map", command=self.open_map_popup).grid(row=0, column=3,
                                                                                         pady=10)

    def set_current_time(self):
        """Set the current time in the time fields."""
        now = datetime.now()
        self.hours.set(f"{now.hour:02d}")
        self.minutes.set(f"{now.minute:02d}")
        self.seconds.set(f"{now.second:02d}")

    def calendar_call(self):
        self.cal_popup = tk.Toplevel(self.root)
        self.cal_popup.title("Select Date")
        self.cal_popup.geometry("300x300")
        self.cal = Calendar(self.cal_popup, selectmode="day")
        self.cal.pack(fill=tk.BOTH, expand=True)
        tk.Button(self.cal_popup, text="OK", command=self.choose_calendar).pack(pady=10)

    def clear_placeholder(self, entry, placeholder):
        """Clear placeholder text when the entry is focused."""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def set_placeholder(self, entry, placeholder):
        """Set placeholder text when the entry is unfocused."""
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg='gray')

    def choose_calendar(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.config(fg='black')
        self.date_entry.insert(0, self.cal.selection_get())
        self.cal_popup.withdraw()

    def open_map_popup(self):
        """Open a pop-up map for selecting location."""
        self.map_window = tk.Toplevel(self.root)
        self.map_window.title("Select Location on Map")
        self.map_window.geometry("600x450")

        self.map_widget = TkinterMapView(self.map_window, width=600, height=400)
        self.map_widget.pack(fill=tk.BOTH, expand=True)
        user_lat, user_lon = self.get_user_location()
        self.map_widget.set_position(user_lat, user_lon, zoom=13)
        self.map_widget.add_left_click_map_command(self.on_map_click)

        tk.Button(self.map_window, text="OK", command=self.close_map).pack(pady=10)

    def close_map(self):
        messagebox.showinfo("Location Selected",
                f"Latitude: {self.clicked_lat}\nLongitude: {self.clicked_lon}\nLocation: {self.city_country}")
        self.map_window.withdraw()

    def on_map_click(self, event):
        """Handle map clicks to update location."""
        self.clicked_lat, self.clicked_lon = event
        self.lat_entry.delete(0, tk.END)
        self.lat_entry.insert(0, self.clicked_lat)
        self.lat_entry.config(fg='black')
        self.lon_entry.delete(0, tk.END)
        self.lon_entry.insert(0, self.clicked_lon)
        self.lon_entry.config(fg='black')
        self.map_widget.set_position(
            self.clicked_lat,
            self.clicked_lon,
            zoom=1,
            reset_view=True,
            update_map=True,
        )
        # Reverse geocode to get city and country
        geolocator = Nominatim(user_agent="novaspace")
        location = geolocator.reverse((self.clicked_lat, self.clicked_lon), language="en")
        if location and location.raw.get("address"):
            address = location.raw["address"]
            city = address.get("city", "Unknown City")
            country = address.get("country", "Unknown Country")
            self.city_country = f"{city}, {country}"
        else:
            self.city_country = "Unknown Location"

        # Update the map marker
        if self.current_marker:
            self.map_widget.delete(self.current_marker)
        self.current_marker = self.map_widget.set_marker(
            self.clicked_lat,
            self.clicked_lon,
            text=f"{self.city_country}\nLat: {self.clicked_lat:.4f}, Lon: {self.clicked_lon:.4f}",
        )

    def select_random_star(self, n=1, obs=False):
        """Select a random star."""
        try:
            if n == 1:
                custom_simbad = Simbad()
                custom_simbad.TIMEOUT = 10
                custom_simbad.ROW_LIMIT = 50
                query_result = custom_simbad.query_criteria("cat=HIP")
                if query_result is None or len(query_result) == 0:
                    messagebox.showerror("Error", "No stars found in Simbad database.")
                    return
                random_star = random.choice(query_result["MAIN_ID"])
                self.star_entry.delete(0, tk.END)
                self.star_entry.insert(0, random_star)
                self.star_entry.config(fg='black')
                return random_star
            elif n != 1 & obs == False:
                if n > 50:
                    messagebox.showerror("Error",
                                         "Number of stars cannot be greater than 50\n Please try again with a lower number of stars.")
                    return ValueError
                custom_simbad = Simbad()
                custom_simbad.TIMEOUT = 10
                custom_simbad.ROW_LIMIT = n
                query_result = custom_simbad.query_criteria("cat=HIP")
                return query_result["MAIN_ID"]
            elif n != 1 & obs == True:
                if n > 50:
                    messagebox.showerror("Error",
                                         "Number of stars cannot be greater than 50\n Please try again with a lower number of stars.")
                    return ValueError
                custom_simbad = Simbad()
                custom_simbad.TIMEOUT = 10
                custom_simbad.ROW_LIMIT = 50
                query_result = custom_simbad.query_criteria("cat=HIP")
                return query_result["MAIN_ID"]

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch random star.\n{e}")

    def timezone_offset(self):
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=self.clicked_lon, lat=self.clicked_lat)
        if timezone_str:
            timezone = pytz.timezone(timezone_str)
            offset = datetime.now(timezone).utcoffset().total_seconds() / 3600
            return offset
        return 0

    def calculate_observation(self):
        """Perform observation calculations."""
        try:
            lat = float(self.lat_entry.get())
            date = self.date_entry.get()
            time = [int(self.hours.get()), int(self.minutes.get()), int(self.seconds.get())]
            self.lct_observer = time[0] + time[1] / 60 + time[2] / 3600
            self.JD = self.JulianDay(date, time)
            if self.options.get() == "Single Star":
                star_name = self.star_entry.get()
                star = SkyCoord.from_name(star_name)
                ra = star.ra.hour
                dec = star.dec.degree

                lst_rise, lst_set = self.obs_star(lat, ra, dec)
                self.process_single_star(star_name, lst_rise, lst_set)
            elif self.options.get() == "Multiple Stars":
                self.obs = self.obs_only.get() == 1
                num_stars = int(self.num_stars_entry.get())
                stars = self.select_random_star(num_stars)
                self.process_multiple_stars(lat, stars, date, time)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input.\n{e}")

    def obs_star(self, lat, right_ascension, delta):
        Ar = math.sin(math.radians(delta)) / math.cos(math.radians(lat))
        H1 = math.tan(math.radians(delta)) * math.tan(math.radians(lat))
        if abs(Ar) < 1 and abs(H1) < 1:
            h = math.degrees(math.acos(-H1)) / 15
            rise = (24 + right_ascension - h) % 24
            set_time = (right_ascension + h) % 24
            return rise, set_time
        else:
            return None, None

    def JulianDay(self, date, time):
        hour = time[0]
        minute = time[1]
        second = time[2]
        year = int(date.split("-")[0])
        month = int(date.split("-")[1])
        day = int(date.split("-")[2])
        if year < -4712:
            messagebox.showerror("Error", "Year must be higher than -4712.")
        if (month < 1 or month > 12) or (day <= 0):
            messagebox.showerror("Error", "Invalid month or day.")

        if month < 3:
            month += 12
            year -= 1

        A = int(year / 100)
        B = 2 - A + int(A / 4)
        JD = (1720994.5 + int(365.25 * year) + int(30.6001 * (month + 1)) + day + B
              + (hour + minute / 60 + second / 3600) / 24)
        return JD

    def lst_to_lct(self, lst, JD, offset):
        gst = lst - (self.clicked_lon / 15)
        gst %= 24
        S = JD - 2451545.0
        T = S / 36525.0
        gst_0 = 6.697374558 + (2400.051336 * T) + (0.000025862 * T ** 2)
        gst_0 %= 24
        ut = (gst - gst_0) * 0.9972695663
        if ut < 0:
            ut += 24
        lct = ut + offset
        lct %= 24
        return lct

    def is_observe(self, LCT_observer, LCT_rise, LCT_set):
        return LCT_rise <= LCT_observer <= LCT_set

    def convert_dec_to_hours(self, decimal_time):
        hours = int(decimal_time)
        minutes = int((decimal_time - hours) * 60)
        seconds = int(((decimal_time - hours) * 60 - minutes) * 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def process_single_star(self, star_name, lst_rise, lst_set):
        """Process a single star observation."""
        try:
            lct_rise = self.lst_to_lct(lst_rise, self.JD, self.timezone_offset())
            lct_set = self.lst_to_lct(lst_set, self.JD, self.timezone_offset())
            is_observe = "Observable" if self.is_observe(self.lct_observer, lct_rise, lct_set) else "Unobservable"
            timezone = "GMT +" + str(self.timezone_offset()) if self.timezone_offset() > 0 else "GMT " + str(
                self.timezone_offset())
            lct_obs = self.convert_dec_to_hours(self.lct_observer)
            lct_set = self.convert_dec_to_hours(lct_set)
            lct_rise = self.convert_dec_to_hours(lct_rise)
            result_window = tk.Toplevel(self.root)
            result_window.title("Observation")
            result_window.geometry("400x300")
            bg_color = "#2C3E50"  # Dark blue-gray background
            result_window.configure(bg=bg_color)
            heading = tk.Label(
                result_window,
                text=f"{star_name} Observability",
                font=("Helvetica", 16, "bold"),
                fg="#ECF0F1",  # Light text color
                bg=bg_color
            )
            heading.pack(pady=10)

            details = (

                f"Local Observation Time: {lct_obs} ({timezone})\n"
                f"Rise Time: {lct_rise} ({timezone})\n"
                f"Set Time: {lct_set} ({timezone})"
            )
            details_label = tk.Label(
                result_window,
                text=details,
                justify="left",
                wraplength=350,
                fg="#ECF0F1",  # Light text color
                bg=bg_color,  # Matches background
                font=("Helvetica", 12)
            )
            details_label.pack(pady=10)
            observability_color = "#27AE60" if is_observe == "Observable" else "#E74C3C"
            observability_label = tk.Label(
                result_window,
                text=f"Observability: {is_observe}",
                font=("Helvetica", 12, "bold"),
                fg=observability_color,
                bg=bg_color
            )
            observability_label.pack(pady=10)

            close_button = tk.Button(
                result_window,
                text="Close",
                command=result_window.destroy,
                bg="#2980B9",  # Blue button
                fg="white",  # White text on button
                font=("Helvetica", 12, "bold")
            )
            close_button.pack(pady=10)


        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch star coordinates.\n{e}")

    def process_multiple_stars(self, lat, stars, date, time):
        """Process multiple stars observation."""
        try:
            data = []
            timezone = "GMT +" + str(self.timezone_offset()) if self.timezone_offset() > 0 else "GMT " + str(
                self.timezone_offset())
            messagebox.showinfo("Observating...",
                                f"Processing {len(stars)} stars\n This may take a while\n Please Wait.")
            if self.obs == False:
                for star in stars:
                    ra = SkyCoord.from_name(star).ra.hour
                    dec = SkyCoord.from_name(star).dec.degree
                    lst_rise, lst_set = self.obs_star(lat, ra, dec)
                    lct_rise = self.lst_to_lct(lst_rise, self.JD, self.timezone_offset())
                    lct_set = self.lst_to_lct(lst_set, self.JD, self.timezone_offset())
                    is_observe = "Observable" if self.is_observe(self.lct_observer, lct_rise,
                                                                 lct_set) else "Unobservable"
                    lct_rise = self.convert_dec_to_hours(lct_rise)
                    lct_set = self.convert_dec_to_hours(lct_set)
                    lct_obs = self.convert_dec_to_hours(self.lct_observer)
                    data.append([star, lct_rise, lct_obs, lct_set, is_observe])
            else:
                for star in stars:
                    ra = SkyCoord.from_name(star).ra.hour
                    dec = SkyCoord.from_name(star).dec.degree
                    lst_rise, lst_set = self.obs_star(lat, ra, dec)
                    lct_rise = self.lst_to_lct(lst_rise, self.JD, self.timezone_offset())
                    lct_set = self.lst_to_lct(lst_set, self.JD, self.timezone_offset())
                    observable = self.is_observe(self.lct_observer, lct_rise, lct_set)
                    lct_rise = self.convert_dec_to_hours(lct_rise)
                    lct_set = self.convert_dec_to_hours(lct_set)
                    lct_obs = self.convert_dec_to_hours(self.lct_observer)
                    if observable == True:
                        data.append([star, lct_rise, lct_obs, lct_set, "Observable"])

            if data == []:
                messagebox.showinfo("Observation",
                                    f"No stars are observable at {self.lct_observer} {timezone}")
                return
            else:
                # Create a new window for displaying results
                result_window = tk.Toplevel(self.root)
                result_window.geometry("1200x600")
                result_window.title(f"Stars Observation Results in {time[0]}:{time[1]}:{time[2]} {timezone} at {date}")

                # Create a Treeview widget
                tree = ttk.Treeview(result_window,
                                    columns=("Star", "LCT Rise", "LCT Observer", "LCT Set", "Observability"),
                                    show='headings')
                tree.heading("Star", text="Star")
                tree.heading("LCT Rise", text=f"LCT Rise ({timezone})")
                tree.heading("LCT Observer", text=f"LCT Observer ({timezone})")
                tree.heading("LCT Set", text=f"LCT Set ({timezone})")
                tree.heading("Observability", text="Observability")
                for star_data in data:
                    tree.insert("", tk.END, values=star_data)
                tree.pack(expand=True, fill=tk.BOTH)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process stars.\n{e}")

    def reset_inputs(self):
        """Reset all inputs and results."""
        self.update_mode(self.options.get())
        self.result_label.config(text="")


# Run the application
root = tk.Tk()
app = StarObservationApp(root)
root.mainloop()
