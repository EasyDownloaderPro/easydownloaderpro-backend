from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.get_json()
    video_url = data.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        # yt-dlp options
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'force_generic_extractor': False,
            'simulate': True,
            'extract_flat': 'in_playlist',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            # Try to find video URL
            if 'url' in info:
                download_link = info['url']
            elif 'entries' in info and len(info['entries']) > 0:
                download_link = info['entries'][0]['url']
            else:
                return jsonify({'error': 'Unable to extract video link'}), 500

        return jsonify({'success': True, 'download_url': download_link})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
