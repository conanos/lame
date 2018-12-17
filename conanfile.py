from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conanos.build import config_scheme
import os, shutil

class LameConan(ConanFile):
    name = "lame"
    version = "3.100"
    description = "LAME is a high quality MPEG Audio Layer III (MP3) encoder licensed under the LGPL"
    url = "https://github.com/conanos/lame"
    homepage = "http://lame.sourceforge.net/"
    license = "LGPL"
    exports = ["COPYING"]
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def source(self):
        url_ = 'https://github.com/CentricularK/lame/archive/RELEASE__{version}.tar.gz'
        tools.get(url_.format(version=self.version.replace('.','_')))
        "lame-RELEASE__3_100"
        extracted_dir = self.name + "-RELEASE__" + self.version.replace('.','_')
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        #with tools.chdir(self.source_subfolder):
        #    self.run("autoreconf -f -i")

        #    autotools = AutoToolsBuildEnvironment(self)
        #    _args = ["--prefix=%s/builddir"%(os.getcwd()), "--disable-frontend", "--disable-decoder"]
        #    if self.options.shared:
        #        _args.extend(['--enable-shared=yes','--enable-static=no'])
        #    else:
        #        _args.extend(['--enable-shared=no','--enable-static=yes'])
        #    autotools.configure(args=_args)
        #    autotools.make(args=["-j4"])
        #    autotools.install()
        if self.settings.os == 'Windows':
            with tools.chdir(os.path.join(self._source_subfolder,"SMP")):
                msbuild = MSBuild(self)
                build_type = str(self.settings.build_type) + ("DLL" if self.options.shared else "")
                msbuild.build("libmp3lame.sln",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'},build_type=build_type)

    def package(self):
        if self.settings.os == 'Windows':
            platforms={'x86': 'Win32', 'x86_64': 'x64'}
            rplatform = platforms.get(str(self.settings.arch))
            self.copy("*", dst=os.path.join(self.package_folder,"include"), src=os.path.join(self.build_folder,"..", "msvc","include"))
            if self.options.shared:
                for i in ["lib","bin"]:
                    self.copy("*", dst=os.path.join(self.package_folder,i), src=os.path.join(self.build_folder,"..","msvc",i,rplatform))
            self.copy("*", dst=os.path.join(self.package_folder,"licenses"), src=os.path.join(self.build_folder,"..", "msvc","licenses"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
