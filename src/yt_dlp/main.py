import dagger
from dagger import dag, function, object_type


@object_type
class YtDlp:
    DEFAULT_FORMAT = "bestvideo[ext=mp4]+bestaudio[ext=m4a]"
    @function
    def base(self) -> dagger.Container:
        """Returns base yt-dlp Container"""
        return (
            dag.container()
            .from_("python:latest")
            .with_exec(["pip", "install", "yt-dlp"])
            .with_exec(["apt", "update", "-y"])
            .with_exec(["apt", "install", "ffmpeg", "-y"]) # needed to merge vid+aud
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
