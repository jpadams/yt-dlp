import dagger
from dagger import dag, function, object_type


@object_type
class YtDlp:
    DEFAULT_FORMAT = "bestvideo[ext=mp4]+bestaudio[ext=m4a]"
    @function
    def base(self) -> dagger.Container:
        """Returns base yt-dlp Container"""
        ffmpeg_script = '''ARCH=$(dpkg --print-architecture)
case "$ARCH" in
amd64)  A=ffmpeg-master-latest-linux64-gpl.tar.xz ;;
arm64)  A=ffmpeg-master-latest-linuxarm64-gpl.tar.xz ;;
*)      echo "Unsupported arch: $ARCH" && exit 1 ;;
esac

curl -L "https://github.com/yt-dlp/FFmpeg-Builds/releases/latest/download/$A" | tar -xJ --strip-components=2 -C /usr/local/bin --wildcards */ffmpeg */ffprobe'''

        return (
            dag.container()
            .from_("python:latest")
            .with_exec(["pip", "install", "yt-dlp"])
            .with_exec(["apt", "update", "-y"])
            .with_exec(["apt", "install", "curl", "xz-utils", "-y"])
            .with_exec(["bash", "-c", ffmpeg_script])
            .with_workdir("/dl")
        )

    @function
    def dl(self, url: str, format: str = DEFAULT_FORMAT, name: str = "out.mp4", sections: str = "") -> dagger.File:
        """Returns a downloaded video File"""
        cmd = (
            f"/usr/local/bin/yt-dlp -o {name} -f {format} "
            f"{'--download-sections ' + sections if sections else ''}"
            f" --merge-output-format mp4 {url}"
        )
        return (
            self.base()
            .with_exec(["bash", "-c", cmd])
            .file(f"/dl/{name}")
        )
