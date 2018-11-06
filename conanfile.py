from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from shutil import copyfile
import os

class LameConan(ConanFile):
    name = "lame"
    version = "3.100"
    description = "LAME is a high quality MPEG Audio Layer III (MP3) encoder licensed under the LGPL"
    url = "https://github.com/conanos/lame"
    license = "GPL"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    source_subfolder = "source_subfolder"

    def source(self):
        url_ = 'http://downloads.sourceforge.net/project/{name}/{name}/{version}/{name}-{version}.tar.gz'.format(name=self.name, version=self.version)
        tools.get(url_)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        with tools.chdir(self.source_subfolder):
            self.run("autoreconf -f -i")

            autotools = AutoToolsBuildEnvironment(self)
            _args = ["--prefix=%s/builddir"%(os.getcwd()), "--disable-frontend", "--disable-decoder"]
            if self.options.shared:
                _args.extend(['--enable-shared=yes','--enable-static=no'])
            else:
                _args.extend(['--enable-shared=no','--enable-static=yes'])
            autotools.configure(args=_args)
            autotools.make(args=["-j4"])
            autotools.install()

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

