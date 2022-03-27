from crawler import ProxyManager, WebCrawler
from video import Video, QueryInfo, VideoInfo, VideoNotFoundException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class VideoCrawler(WebCrawler):
    def __init__(self, headless=True, show_images=False, index=0):
        self.__headless = headless
        self.__show_images = show_images
        self.proxy_manager = ProxyManager()
        self.index = index
        self.rotate_proxy()

    def rotate_proxy(self):
        if hasattr(self, "driver"):
            super().__del__()
        super().__init__(
            self.proxy_manager.proxy, self.__headless, self.__show_images, self.index
        )

    @property
    def knowledge_panel(self):
        return self.driver.find_element_by_xpath('//div[@jscontroller="cSX9Xe"]')

    def get_video(self, video: Video, index):
        try:
            ## Generate query for video
            query = video.query

            search_location = None

            def search_video():
                ## Search for video
                self.driver.get("https://www.google.com")
                self.wait_for_document()

                ## Accept cookies
                agree_element = self.driver.find_elements_by_xpath(
                    '//div[contains(string(), "I agree") and contains(@class, "QS5gu")]'
                )
                if (
                    self.exec_script(
                        "js/findText.js", "Before you continue to Google Search"
                    )
                    is not None
                    and len(agree_element) != 0
                ):
                    self.click_element(agree_element[0])

                self.driver.save_screenshot("vid.png")
                search_bar = self.driver.find_element_by_name("q")
                search_bar.send_keys(query.query)
                search_bar.submit()
                self.wait_for_document()
                nonlocal search_location
                search_location = self.driver.current_url

                if search_location.startswith("https://www.google.com/sorry"):
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: len(
                            self.driver.find_elements_by_class_name("captcha-solver")
                        )
                        > 0
                    )

                    # Try captcha 5 times
                    for i in range(0, 5):
                        self.driver.find_element_by_class_name("captcha-solver").click()
                        WebDriverWait(self.driver, 200).until(
                            lambda driver: driver.current_url != search_location
                            or self.exec_script("js/checkCaptchaError.js")
                        )
                        if not self.exec_script("js/checkCaptchaError.js"):
                            break
                        else:
                            print("Captcha failed, retrying")
                            if i == 4:
                                raise Exception("Captcha failed 5 times, abort")

                    self.wait_for_document()

            search_video()

            ## Click on imdb link on knowledge panel
            imdb_url = None

            def click_imdb_link():
                def find_imdb_link():
                    try:
                        return self.exec_script(
                            "js/findLink.js",
                            r"https://www.imdb.com/title/.+/",
                            self.knowledge_panel,
                        )
                    except NoSuchElementException:
                        return None

                imdb_link = find_imdb_link()
                if imdb_link is None:

                    def attempt_next_query():
                        query.next_query()
                        if query.query is not None:
                            search_video()
                        else:
                            self.driver.save_screenshot("ERROR_" + query.title + ".png")
                            raise VideoNotFoundException()

                    # Check if this is a series if imdb link is not found
                    movie_links = self.driver.find_elements_by_css_selector(
                        'wp-grid-view [data-attrid="kc:/film/film_series:films"]'
                    )
                    if len(movie_links) > 0:
                        ## If film series and no year is given, use first film
                        print("Warning: Used first film without year")
                        self.click_element(movie_links[0])
                        try:
                            WebDriverWait(self.driver, 20).until(
                                lambda driver: find_imdb_link() is not None
                            )
                        except TimeoutException:
                            attempt_next_query()
                        return click_imdb_link()
                    else:
                        attempt_next_query()
                        return click_imdb_link()
                else:
                    nonlocal imdb_url
                    imdb_url = imdb_link.get_attribute("href")

                self.click_element(imdb_link)
                self.wait_for_document()

            click_imdb_link()

            ## Save imdb info
            description = self.driver.find_element_by_class_name(
                "GenresAndPlot__TextContainerBreakpointXL-cum89p-2"
            ).get_attribute("textContent")
            imdb_title = self.driver.find_element_by_class_name(
                "TitleHeader__TitleText-sc-1wu6n3d-0"
            ).get_attribute("textContent")
            rating = self.driver.find_element_by_class_name(
                "AggregateRatingButton__RatingScore-sc-1ll29m0-1"
            ).get_attribute("textContent")
            film_length = self.exec_script("js/getFilmLength.js")
            release_info = self.exec_script("js/getYears.js")
            parental_rating = self.exec_script("js/getParentalRating.js")
            genres = self.exec_script("js/getIMDbCredits.js", r"Genres?")
            directors = self.exec_script("js/getIMDbCredits.js", r"Directors?")
            writers = self.exec_script("js/getIMDbCredits.js", r"Writers?")
            stars = self.exec_script("js/getIMDbCredits.js", r"Stars?")

            ## Click on poster image
            poster_image_link = self.driver.find_element_by_css_selector(
                ".Poster__CelPoster-sc-6zpm25-0 .ipc-lockup-overlay"
            )
            self.click_element(poster_image_link)
            self.wait_for_document()

            ## Save poster image
            imdb_poster_query = self.driver.find_elements_by_class_name(
                "MediaViewerImagestyles__PortraitImage-sc-1qk433p-0"
            )
            poster_image = None
            if len(imdb_poster_query) > 0:
                poster_image = imdb_poster_query[0]
            else:
                ## Backtrack to knowledge panel
                self.driver.get(search_location)
                self.wait_for_document()
                # Get google image link
                image_link = self.driver.find_element_by_css_selector(".kAOS0")
                self.click_element(image_link)
                self.wait_for_document()

                # Get google image current featured image
                feature_image = self.driver.find_element_by_css_selector(
                    '[jsname="CGzTgf"] [jsname="HiaYvf"]'
                )
                poster_image = feature_image

            img_loc = "images/{:05}_{}.png".format(
                index, query.title.replace("\\", "").replace("/", "")
            )
            self.save_image(poster_image, img_loc)

            return VideoInfo(
                **{
                    "description": description,
                    "imdb_title": imdb_title,
                    "directors": directors,
                    "writers": writers,
                    "stars": stars,
                    "genres": genres,
                    "rating": rating,
                    "film_length": film_length,
                    "parental_rating": parental_rating,
                    "release_info": release_info,
                    "image": img_loc,
                    "imdb_url": imdb_url,
                }
            )
        finally:
            self.rotate_proxy()


"""
first 1000 (or so) only have
description
directors
stars
image
imdb_url

next have these
description
directors
stars
image
imdb_url
rating      (rating /10 by community)
genres
release_info (when it was released/when the series aired)
parental_rating (G/R/PG/etc)
imdb_title
film_length

*** REFETCH ALL THAT NEED TO BE REFETCHED (needrefetch.txt) ***
ALSO FIX ALL MOVIES THAT SHARE THE SAME QUERY AS THIS LIST AS THEY WILL GET THE SAME INFO

[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 74, 75, 76, 77, 78, 79, 80, 81, 83, 84, 85, 86, 87, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 213, 215, 218, 219, 220, 222, 228, 231, 232, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 402, 403, 404, 406, 407, 408, 410, 411, 412, 413, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 515, 516, 517, 518, 519, 520, 521, 522, 523, 526, 527, 528, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 563, 564, 565, 567, 569, 616, 642, 643, 652, 660, 666, 668, 669, 671, 672, 676, 679, 685, 703, 741, 881, 1000, 1001, 1002, 1003, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1022, 1023, 1024, 1025, 1026, 1028, 1030, 1031, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 1062, 1064, 1066, 1067, 1071, 1072, 1073, 1075, 1076, 1078, 1079, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1114, 1115, 1116, 1117, 1118, 1120, 1121, 1122, 1123, 1124, 1125, 1126, 1128, 1129, 1130, 1131, 1132, 1133, 1134, 1136, 1137, 1138, 1139, 1140, 1141, 1142, 1143, 1144, 1145, 1146, 1150, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1163, 1167, 1168, 1169, 1170, 1171, 1172, 1173, 1176, 1177, 1178, 1179, 1180, 1181, 1182, 1183, 1184, 1185, 1186, 1187, 1188, 1189, 1190, 1191, 1192, 1193, 1195, 1196, 1202, 1206, 1210, 1266, 1275, 1284, 1340, 1403, 1550, 1564, 1630, 1632, 1641, 1644, 1658, 1671, 1681, 1704, 1707, 1708, 1710, 1711, 1716, 1832, 1873, 1910, 2021, 2023, 2255, 2256, 2257, 2258, 2259, 2260, 2310, 2338, 2426, 2460, 2555, 2682, 2791, 2792, 2900, 2909, 2910, 2977, 3267, 3320, 3342, 3344, 3420, 3421, 3582, 3664, 3738, 4105, 4180, 4188, 4269, 4478, 4519, 4609, 4611, 4612, 4615, 4619, 4647, 4650, 4812, 4974, 4975, 4976, 4977, 4978, 4979, 5475, 5491, 5553, 5790, 6037, 6264, 6419, 6437, 6449, 6452, 6670, 6727, 7022]
"""
