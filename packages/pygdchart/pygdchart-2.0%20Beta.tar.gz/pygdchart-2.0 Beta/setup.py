from distutils.core import setup, Extension

#GDCHART_PATH = "../gdchart0.11.4dev"
#GD_PATH = "../gd-1.8.4"
setup(
            name="pygdchart",
            version="2.0 Beta",
            description="Python bindings to the GDChart library",
            author="Nullcube Pty Ltd",
            author_email="aldo@nullcube.com",
            url="http://www.nullcube.com",
            py_modules = ["gdchart"],
            ext_modules=[
                            Extension(
                                        "_gdchartc",
                                        ["_gdchartc.c"],
#                                        include_dirs=[GDCHART_PATH],
                                        library_dirs=[
#                                                            GD_PATH,
#                                                            GDCHART_PATH,
                                                            "/usr/local/lib",
                                                            "/usr/X11R6/lib",
                                                            "/usr/lib"
                                                    ],
                                        define_macros=[
                                                            ("HAVE_LIBFREETYPE", 1),
                                                            ("HAVE_JPEG", 1),
                                                        ],
                                        libraries=["gdc", "gd", "png", "z", "jpeg", "freetype"]
                            )
                        ]
    )
