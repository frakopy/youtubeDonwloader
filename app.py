from pytubefix import YouTube
import streamlit as st
import moviepy.editor as mpe
import os


class YouTubeDownloader:
    def __init__(self, url):
        self.url = url
        self.youtube =  YouTube(self.url)
        self.stream = None

    def get_file_size(self):
        self.stream = self.youtube.streams.filter(subtype="mp4", res="1080p").first() 
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
        with open(file_name, "rb") as file:
            st.download_button(
                label="Download",
                data=file,
                file_name=file_name,
            )
        
        os.remove(file_name) # Remove file from local storage


    def start_download(self):
        with st.spinner('Preparing download please wait...'):
            st.session_state["filename"] = ""
            if self.download_type == "Video and audio":
                vname = "clip.mp4"
                aname = "audio.mp3"

                # Download video and rename
                video = self.youtube.streams.filter(subtype="mp4", res="1080p").first().download()
                os.rename(video, vname)

                # Download audio and rename
                audio = self.youtube.streams.filter(only_audio=True).first().download()
                os.rename(audio, aname)

                # Setting the audio to the video
                video = mpe.VideoFileClip(vname)
                audio = mpe.AudioFileClip(aname)
                final = video.set_audio(audio)

                # Output result
                st.session_state["filename"] = os.path.join(
                    "video", f"{self.youtube.title}.mp4"
                )
                final.write_videofile(st.session_state["filename"])

                # Delete video and audio to keep the result
                os.remove(vname)
                os.remove(aname)
            else:
                # Download audio and rename
                audio = self.youtube.streams.filter(only_audio=True).first()
                st.session_state["filename"] = os.path.join(
                    "audio", f"{self.youtube.title}.mp3"
                )
                audio.download(filename=st.session_state["filename"])

        st.success("Your file is ready to be downloaded")
        self.download(st.session_state["filename"])  # It will be downloaded to your default 'Downloads' directory


if __name__ == "__main__":
    st.title("YouTube Downloader \U0001F4E5")
    url = st.text_input("Please enter a valid youtube url")

    if url:
        downloader = YouTubeDownloader(url)
        downloader.get_permission_to_continue()
