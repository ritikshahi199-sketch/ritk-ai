import os
from flask import Flask, jsonify, render_template_string, request
from groq import Groq

app = Flask(__name__)

# Server ke environment variable se secure tarike se API key uthayega
API_KEY = os.environ.get("GROQ_API_KEY")


def get_client():
  if not API_KEY:
    return None
  return Groq(api_key=API_KEY)


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Ritik Assistant Pro</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .glow-effect { box-shadow: 0 0 20px rgba(59, 130, 246, 0.15); }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 h-[100dvh] flex overflow-hidden font-sans">

    <!-- Sidebar Overlay for Mobile -->
    <div id="sidebar-overlay" onclick="toggleSidebar()" class="fixed inset-0 bg-black/60 z-30 hidden md:hidden transition-opacity"></div>

    <!-- Sidebar for Chat History -->
    <div id="sidebar" class="fixed md:static inset-y-0 left-0 bg-slate-900 border-r border-slate-800 w-72 flex flex-col transition-transform duration-300 -translate-x-full md:translate-x-0 z-40 shadow-2xl">
        <div class="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
            <span class="font-bold text-yellow-400 flex items-center gap-2"><i class="fa-solid fa-clock-rotate-left"></i> Chat History</span>
            <button onclick="toggleSidebar()" class="text-slate-400 hover:text-white md:hidden cursor-pointer p-1"><i class="fa-solid fa-xmark text-lg"></i></button>
        </div>
        
        <div class="p-3">
            <button onclick="startNewChat()" class="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 p-2.5 rounded-xl text-sm font-medium flex items-center gap-2 transition-colors cursor-pointer">
                <i class="fa-solid fa-plus text-yellow-400"></i> New Chat
            </button>
        </div>

        <div id="history-list" class="flex-1 overflow-y-auto px-3 space-y-2 text-sm text-slate-300"></div>
        <div class="p-4 border-t border-slate-800 text-xs text-slate-500 text-center bg-slate-900/50">
            Ritik Assistant Pro &bull; Secure v4.0
        </div>
    </div>

    <!-- Main Chat Section -->
    <div class="flex-1 flex flex-col h-[100dvh] relative bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 w-full overflow-hidden">
        
        <!-- Header -->
        <header class="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 p-3 md:p-4 flex items-center justify-between shadow-lg z-10 shrink-0">
            <div class="flex items-center gap-2 md:gap-3">
                <button onclick="toggleSidebar()" class="text-slate-300 hover:text-white text-lg p-2 cursor-pointer transition-colors"><i class="fa-solid fa-bars"></i></button>
                <h1 class="text-base md:text-lg font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-amber-200 flex items-center gap-2">
                    <i class="fa-solid fa-bolt text-yellow-400"></i> Ritik Assistant
                </h1>
            </div>
            
            <div class="flex items-center gap-3">
                <select id="lang-select" class="bg-slate-800 text-slate-200 border border-slate-700 text-xs rounded-lg px-2 py-1.5 focus:outline-none focus:border-blue-500 cursor-pointer">
                    <option value="hi">🇮🇳 Hindi</option>
                    <option value="en">🇬🇧 English</option>
                </select>
                <div class="hidden sm:flex items-center gap-2">
                    <span class="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span class="text-xs text-slate-400 font-medium">Ritik Sir</span>
                </div>
            </div>
        </header>

        <!-- Chat Container -->
        <div id="chat-container" class="flex-1 overflow-y-auto p-3 md:p-6 space-y-4 md:space-y-6 max-w-4xl w-full mx-auto">
            <div class="flex items-start space-x-3">
                <div class="bg-gradient-to-tr from-blue-600 to-indigo-600 text-white rounded-2xl h-8 w-8 md:h-10 md:w-10 flex items-center justify-center font-bold text-xs md:text-sm shadow-lg shadow-blue-500/20 shrink-0">AI</div>
                <div class="bg-slate-900/90 border border-slate-800 p-3.5 md:p-4 rounded-2xl max-w-[85%] md:max-w-2xl text-xs md:text-sm shadow-xl leading-relaxed glow-effect">
                    Hello main Ritik, main ek AI hoon. Main aapki kya madad kar sakta hoon?
                </div>
            </div>
        </div>

        <!-- Image Preview Area -->
        <div id="preview-container" class="max-w-4xl mx-auto w-full px-3 md:px-4 hidden mb-2 shrink-0">
            <div class="relative inline-block bg-slate-900 p-2 rounded-xl border border-slate-800 shadow-lg">
                <img id="image-preview" class="h-16 md:h-20 rounded-lg object-cover">
                <button onclick="removeImage()" class="absolute -top-2 -right-2 bg-red-600 text-white rounded-full h-5 w-5 md:h-6 md:w-6 flex items-center justify-center text-xs shadow-md cursor-pointer hover:bg-red-700 transition-colors"><i class="fa-solid fa-xmark"></i></button>
            </div>
        </div>

        <!-- Input Form -->
        <div class="bg-slate-900/90 border-t border-slate-800 p-3 md:p-4 shadow-2xl backdrop-blur-md shrink-0">
            <form id="chat-form" class="max-w-4xl mx-auto flex items-center gap-2 md:gap-3 bg-slate-950 border border-slate-800 rounded-2xl px-3 md:px-4 py-2.5 shadow-inner focus-within:border-blue-500 transition-all">
                
                <input type="file" id="image-input" accept="image/*" class="hidden" onchange="previewImage(event)">
                
                <button type="button" onclick="document.getElementById('image-input').click()" class="text-slate-400 hover:text-yellow-400 p-1.5 md:p-2 transition-colors cursor-pointer text-base md:text-lg" title="Upload Photo">
                    <i class="fa-solid fa-circle-plus"></i>
                </button>

                <button type="button" id="mic-btn" onclick="toggleSpeechRecognition()" class="text-slate-400 hover:text-blue-400 p-1.5 md:p-2 transition-colors cursor-pointer text-base md:text-lg" title="Speak">
                    <i class="fa-solid fa-microphone"></i>
                </button>

                <input type="text" id="user-input" placeholder="Type or search here..." autocomplete="off" class="flex-1 bg-transparent border-none px-1 md:px-2 py-1 text-xs md:text-sm focus:outline-none text-slate-100 placeholder-slate-500">
                
                <button type="submit" id="send-btn" class="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white px-4 md:px-6 py-2 md:py-2.5 rounded-xl font-medium text-xs md:text-sm transition-all shadow-lg shadow-blue-600/30 cursor-pointer flex items-center justify-center shrink-0">
                    <i class="fa-solid fa-paper-plane"></i>
                </button>
            </form>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const chatForm = document.getElementById('chat-form');
        const userInput = document.getElementById('user-input');
        const imageInput = document.getElementById('image-input');
        const imagePreview = document.getElementById('image-preview');
        const previewContainer = document.getElementById('preview-container');
        const sidebar = document.getElementById('sidebar');
        const sidebarOverlay = document.getElementById('sidebar-overlay');
        const historyList = document.getElementById('history-list');
        const langSelect = document.getElementById('lang-select');

        let base64Image = null;
        let currentUtterance = null;
        let isSpeaking = false;
        let chatHistoryData = [];

        function toggleSidebar() {
            sidebar.classList.toggle('-translate-x-full');
            sidebarOverlay.classList.toggle('hidden');
        }

        function previewImage(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    base64Image = e.target.result;
                    previewContainer.classList.remove('hidden');
                }
                reader.readAsDataURL(file);
            }
        }

        function removeImage() {
            imageInput.value = '';
            base64Image = null;
            previewContainer.classList.add('hidden');
        }

        function startNewChat() {
            chatContainer.innerHTML = `
                <div class="flex items-start space-x-3">
                    <div class="bg-gradient-to-tr from-blue-600 to-indigo-600 text-white rounded-2xl h-8 w-8 md:h-10 md:w-10 flex items-center justify-center font-bold text-xs md:text-sm shadow-lg shadow-blue-500/20 shrink-0">AI</div>
                    <div class="bg-slate-900/90 border border-slate-800 p-3.5 md:p-4 rounded-2xl max-w-[85%] md:max-w-2xl text-xs md:text-sm shadow-xl leading-relaxed glow-effect">
                        Hello main Ritik, main ek AI hoon. Main aapki kya madad kar sakta hoon?
                    </div>
                </div>
            `;
            if (window.innerWidth < 768) toggleSidebar();
        }

        function addHistoryItem(text) {
            chatHistoryData.unshift(text);
            renderHistory();
        }

        function renderHistory() {
            historyList.innerHTML = '';
            chatHistoryData.forEach((item) => {
                historyList.innerHTML += `
                    <div class="p-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 cursor-pointer truncate transition-all border border-slate-700/50 flex items-center gap-2 text-xs md:text-sm">
                        <i class="fa-solid fa-message text-yellow-400"></i> ${item}
                    </div>
                `;
            });
        }

        function toggleSpeech(text, btnElement) {
            if (!('speechSynthesis' in window)) return;

            if (isSpeaking) {
                window.speechSynthesis.cancel();
                isSpeaking = false;
                btnElement.innerHTML = '<i class="fa-solid fa-volume-high"></i> Sunen';
                btnElement.classList.remove('text-yellow-400');
            } else {
                window.speechSynthesis.cancel();
                currentUtterance = new SpeechSynthesisUtterance(text);
                currentUtterance.lang = langSelect.value === 'hi' ? 'hi-IN' : 'en-US';
                
                isSpeaking = true;
                btnElement.innerHTML = '<i class="fa-solid fa-volume-xmark"></i> Stop';
                btnElement.classList.add('text-yellow-400');

                currentUtterance.onend = () => {
                    isSpeaking = false;
                    btnElement.innerHTML = '<i class="fa-solid fa-volume-high"></i> Sunen';
                    btnElement.classList.remove('text-yellow-400');
                };
                currentUtterance.onerror = () => {
                    isSpeaking = false;
                    btnElement.innerHTML = '<i class="fa-solid fa-volume-high"></i> Sunen';
                    btnElement.classList.remove('text-yellow-400');
                };

                window.speechSynthesis.speak(currentUtterance);
            }
        }

        function toggleSpeechRecognition() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();
                recognition.lang = langSelect.value === 'hi' ? 'hi-IN' : 'en-US';
                
                const micBtn = document.getElementById('mic-btn');
                micBtn.classList.add('text-red-500', 'animate-pulse');

                recognition.onresult = (event) => {
                    userInput.value = event.results[0][0].transcript;
                    micBtn.classList.remove('text-red-500', 'animate-pulse');
                };
                recognition.onerror = () => micBtn.classList.remove('text-red-500', 'animate-pulse');
                recognition.onend = () => micBtn.classList.remove('text-red-500', 'animate-pulse');
                recognition.start();
            }
        }

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = userInput.value.trim();
            if (!message && !base64Image) return;

            addHistoryItem(message || "Photo Query");

            let userHTML = `<div class="flex items-start justify-end space-x-3"><div class="bg-gradient-to-r from-emerald-600 to-teal-600 p-3.5 md:p-4 rounded-2xl max-w-[85%] md:max-w-xl text-xs md:text-sm shadow-xl space-y-2 text-white">`;
            if (base64Image) {
                userHTML += `<img src="${base64Image}" class="h-28 md:h-32 rounded-lg object-cover shadow-md">`;
            }
            if (message) {
                userHTML += `<div>${message}</div>`;
            }
            userHTML += `</div><div class="bg-emerald-700 text-white rounded-2xl h-8 w-8 md:h-10 md:w-10 flex items-center justify-center font-bold text-xs shadow-lg shrink-0">YOU</div></div>`;
            
            chatContainer.innerHTML += userHTML;

            const currentMessage = message;
            const currentLang = langSelect.value;
            userInput.value = '';
            removeImage();
            chatContainer.scrollTop = chatContainer.scrollHeight;

            const loadingId = 'loading-' + Date.now();
            chatContainer.innerHTML += `
                <div id="${loadingId}" class="flex items-start space-x-3">
                    <div class="bg-gradient-to-tr from-blue-600 to-indigo-600 text-white rounded-2xl h-8 w-8 md:h-10 md:w-10 flex items-center justify-center font-bold text-xs md:text-sm shadow-lg shrink-0">AI</div>
                    <div class="bg-slate-900 border border-slate-800 p-3.5 md:p-4 rounded-2xl text-xs md:text-sm animate-pulse text-slate-400">Soch raha hai...</div>
                </div>
            `;
            chatContainer.scrollTop = chatContainer.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: currentMessage, lang: currentLang })
                });
                const data = await response.json();
                
                document.getElementById(loadingId).remove();
                const safeReply = data.reply.replace(/`/g, '\\`').replace(/"/g, '&quot;');

                chatContainer.innerHTML += `
                    <div class="flex items-start space-x-3">
                        <div class="bg-gradient-to-tr from-blue-600 to-indigo-600 text-white rounded-2xl h-8 w-8 md:h-10 md:w-10 flex items-center justify-center font-bold text-xs md:text-sm shadow-lg shrink-0">AI</div>
                        <div class="bg-slate-900/90 border border-slate-800 p-4 md:p-5 rounded-2xl max-w-[85%] md:max-w-2xl text-xs md:text-sm shadow-xl whitespace-pre-wrap leading-relaxed space-y-3 relative glow-effect">
                            <div>${data.reply}</div>
                            <div class="flex justify-end gap-3 pt-3 border-t border-slate-800/80">
                                <button onclick="toggleSpeech(\`${safeReply}\`, this)" class="text-slate-400 hover:text-yellow-400 text-xs flex items-center gap-1.5 cursor-pointer transition-colors" title="Sunen">
                                    <i class="fa-solid fa-volume-high"></i> Sunen
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            } catch (error) {
                document.getElementById(loadingId).remove();
                chatContainer.innerHTML += `
                    <div class="flex items-start space-x-3">
                        <div class="bg-red-600 text-white rounded-2xl h-8 w-8 md:h-10 md:w-10 flex items-center justify-center font-bold text-xs shadow-lg shrink-0">ERR</div>
                        <div class="bg-slate-900 border border-slate-800 p-4 rounded-2xl max-w-xl text-xs md:text-sm text-red-400 shadow-xl">Server connection error!</div>
                    </div>
                `;
            }
            chatContainer.scrollTop = chatContainer.scrollHeight;
        });
    </script>
</body>
</html>
"""


@app.route("/")
def home():
  return render_template_string(HTML_TEMPLATE)


@app.route("/chat", methods=["POST"])
def chat():
  try:
    client = get_client()
    if not client:
      return jsonify({
          "reply": (
              "Error: API Key configure nahi ki gayi hai server par!"
          )
      })

    data = request.json
    user_message = data.get("message", "")
    lang = data.get("lang", "hi")

    if not user_message:
      return jsonify({"reply": "Kripya valid message bhejein."})

    lang_prompt = (
        "Respond in Hindi language."
        if lang == "hi"
        else "Respond in English language."
    )
    system_instruction = (
        "You are Ritik Assistant, a highly intelligent AI created for Ritik"
        f" Shahi. {lang_prompt} Provide accurate details, context, and official"
        " website links when queried."
    )

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_message},
        ],
    )
    return jsonify({"reply": completion.choices[0].message.content})

  except Exception as e:
    return jsonify({"reply": f"Error aaya hai: {str(e)}"})


if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=5000)