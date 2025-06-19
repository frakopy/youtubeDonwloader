from pytubefix import YouTube
import streamlit as st
import moviepy.editor as mpe
import os
import re


class YouTubeDownloader:
    def __init__(self, url):
        self.url = url
        self.youtube = YouTube(self.url)
        self.stream = None

    def get_file_size(self):
        self.stream = (
            self.youtube.streams.filter(progressive=True, file_extension="mp4")
            .order_by("resolution")
            .desc()
            .first()
        )
        file_size = self.stream.filesize / 1000000
        return file_size

    def get_permission_to_continue(self):
        st.write(f"**Title:** {self.youtube.title}")
        st.write(f"**Author:** {self.youtube.author}")
        st.write(f"**Size:** {self.get_file_size():.2f} MB")
        st.write(f"**Resolution:** {self.stream.resolution or 'N/A'}")

        self.download_type = st.radio(
            "**Select what you want to download:**",
            ["Video and audio", "Only audio"],
        )

        if st.button("Start Download"):
            self.start_download()

    def download(self, file_name):
        display_name = os.path.basename(file_name)
        with open(file_name, "rb") as file:
            st.download_button(
                label="Download",
                data=file,
                file_name=display_name,
            )

        os.remove(file_name)  # Remove file from local storage

    def start_download(self):
        def safe_filename(name):
            return re.sub(r'[\\/*?:"<>|]', "", name)

        with st.spinner("Preparing download please wait..."):
            st.session_state["filename"] = ""
            if self.download_type == "Video and audio":
                filename = safe_filename(self.youtube.title) + ".mp4"
                output_dir = "video"
                vname = "clip.mp4"

                # Download video and rename
                video = (
                    self.youtube.streams.filter(
                        subtype="mp4", progressive=False, type="video"
                    )
                    .order_by("resolution")
                    .desc()
                    .first()
                ).download()

                os.rename(video, vname)

                # Download audio and rename
                audio = self.youtube.streams.filter(only_audio=True).first().download()
                audio_ext = os.path.splitext(audio)[1]  # Getting audio extension
                aname = f"audio{audio_ext}"
                os.rename(audio, aname)

                # Setting the audio to the video
                video = mpe.VideoFileClip(vname)
                audio = mpe.AudioFileClip(aname)
                final = video.set_audio(audio)

                # Output result
                final_path = os.path.join(output_dir, filename)
                st.session_state["filename"] = final_path
                final.write_videofile(final_path)

                # Delete video and audio to keep the result
                os.remove(vname)
                os.remove(aname)
            else:
                # Download audio and rename
                audio = self.youtube.streams.filter(only_audio=True).first()
                filename = safe_filename(self.youtube.title) + ".mp3"
                output_dir = "audio"
                audio.download(output_path=output_dir, filename=filename)
                full_path = os.path.join(output_dir, filename)
                st.session_state["filename"] = full_path

        st.success("Your file is ready to be downloaded")
        self.download(
            st.session_state["filename"]
        )  # It will be downloaded to your default 'Downloads' directory


if __name__ == "__main__":
    st.set_page_config(
        page_title="YoutubeDownloader-app",
        page_icon="📽️",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    st.title("YouTube Downloader \U0001f4e5")
    url = st.text_input("Please enter a valid youtube url")

    if url:
        downloader = YouTubeDownloader(url)
        downloader.get_permission_to_continue()
