from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import instaloader
import os

app = Flask(__name__)

# 📁 એક્સટર્નલ ડાઉનલોડ ફોલ્ડર બનાવો
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# 📥 YouTube, Facebook, TikTok માટે
@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.get_json()
    video_url = data.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

        file_name = os.path.basename(filename)

        return jsonify({
            'success': True,
            'download_url': f'/downloads/{file_name}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 📥 Instagram માટે
@app.route('/api/instagram', methods=['POST'])
def download_instagram():
    data = request.get_json()
    url = data.get('url')

    try:
        loader = instaloader.Instaloader(dirname_pattern=DOWNLOAD_FOLDER, save_metadata=False)
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target=shortcode)

        folder_path = os.path.join(DOWNLOAD_FOLDER, shortcode)
        files = os.listdir(folder_path)
        video_file = next((f for f in files if f.endswith('.mp4')), None)

        if video_file:
            return jsonify({
                "success": True,
                "download_url": f"/downloads/{shortcode}/{video_file}"
            })
        else:
            return jsonify({"success": False, "error": "Video not found in post"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 📂 ડાઉનલોડ્સ ફાઈલ સર્વ કરવા માટે
@app.route('/downloads/<path:filename>')
def serve_download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
