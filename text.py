def start_ffmpeg():
    global process
    with process_lock:
        if process:
            try:
                process.kill()
            except:
                pass
        try:
            process = subprocess.Popen(
                [
                    "ffmpeg",
                    "-i", STREAM_URL,
                    "-an",
                    "-f", "rawvideo",
                    "-pix_fmt", "bgr24",
                    "-vf", f"scale={WIDTH}:{HEIGHT}",
                    "pipe:1"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=10**8
            ) if SOURCE_TYPE == "srt" else subprocess.Popen(
                [
                    "ffmpeg",
                    "-re" if SOURCE_TYPE == "srt" else "-nostdin",
                    "-i", VIDEO_PATH,
                    "-an",
                    "-f", "rawvideo",
                    "-pix_fmt", "bgr24",
                    "-vf", f"scale={WIDTH}:{HEIGHT}",
                    "pipe:1",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=10**8,
            )
            print(f"\n🔄 {Fore.LIGHTWHITE_EX}FFmpeg ({SOURCE_TYPE.upper()}) {Back.GREEN}iniciado{Back.RESET}\n")

        except Exception as e:
            safe_log("Falha ao iniciar FFmpeg", e)
            process = None
            time.sleep(2)