# Streamlit UI Custom CSS Styles
# This file provides visual tokens, CSS definitions, and glassmorphic designs to make the Streamlit app feel state-of-the-art.

def get_custom_css():
    return """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <style>
        /* Global Typography and Reset */
        html, body, [class*="css"], .stApp {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0d0f14;
            color: #e2e8f0;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #07090d !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            color: #cbd5e1;
        }

        /* Custom Header Styling */
        .header-container {
            padding: 2.5rem 1.5rem;
            background: linear-gradient(135deg, rgba(13, 15, 20, 0.95) 0%, rgba(20, 24, 33, 0.95) 100%);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            margin-bottom: 2.5rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }

        .header-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(99, 102, 241, 0.05) 0%, transparent 70%);
            pointer-events: none;
        }

        .header-title {
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.03em;
        }

        .header-subtitle {
            font-size: 1.1rem;
            font-weight: 400;
            color: #94a3b8;
            letter-spacing: 0.02em;
        }

        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
            font-weight: 600;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-right: 0.5rem;
        }

        .badge-primary {
            background-color: rgba(99, 102, 241, 0.15);
            color: #818cf8;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }

        .badge-success {
            background-color: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        /* Glassmorphic Card Container */
        .glass-card {
            background: rgba(30, 41, 59, 0.3);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .glass-card:hover {
            border-color: rgba(99, 102, 241, 0.2);
            box-shadow: 0 8px 30px rgba(99, 102, 241, 0.08);
            transform: translateY(-2px);
        }

        .glass-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 0.75rem;
            margin-bottom: 1rem;
        }

        .glass-card-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #f1f5f9;
        }

        .glass-card-subtitle {
            font-size: 0.85rem;
            color: #64748b;
        }

        /* Form Input overrides */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            background-color: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
            color: #f1f5f9 !important;
            transition: border-color 0.2s ease;
        }

        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 1px #6366f1 !important;
        }

        /* Cyber-Terminal Terminal Console */
        .terminal-container {
            background-color: #030712 !important;
            border: 1px solid rgba(244, 63, 94, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.8), 0 4px 12px rgba(0, 0, 0, 0.5);
            position: relative;
            margin-top: 1rem;
        }

        .terminal-header {
            display: flex;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }

        .terminal-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 6px;
            display: inline-block;
        }

        .dot-red { background-color: #ef4444; }
        .dot-yellow { background-color: #f59e0b; }
        .dot-green { background-color: #10b981; }

        .terminal-title {
            font-size: 0.8rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-left: auto;
        }

        .terminal-content {
            max-height: 400px;
            overflow-y: auto;
            font-size: 0.9rem;
            line-height: 1.5;
            color: #38bdf8;
            white-space: pre-wrap;
            word-break: break-all;
        }

        /* Status colors inside terminal */
        .log-error { color: #f43f5e; font-weight: bold; }
        .log-warn { color: #f59e0b; }
        .log-success { color: #34d399; font-weight: bold; }
        .log-info { color: #38bdf8; }
        
        /* Premium Buttons */
        div.stButton > button {
            background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 2rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
        }

        div.stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4) !important;
            background: linear-gradient(90deg, #4f46e5 0%, #4338ca 100%) !important;
        }

        div.stButton > button:active {
            transform: translateY(0px) !important;
        }
        
        /* Secondary Action Buttons (e.g. Danger or Cancel or Add) */
        .sec-button button {
            background: rgba(30, 41, 59, 0.6) !important;
            color: #f1f5f9 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        .sec-button button:hover {
            background: rgba(30, 41, 59, 0.9) !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
        }

        /* Center alignments */
        .center-text {
            text-align: center;
        }
        
        /* Custom tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(15, 23, 42, 0.4);
            padding: 6px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .stTabs [data-baseweb="tab"] {
            height: 40px;
            white-space: pre;
            background-color: transparent;
            border-radius: 8px;
            color: #94a3b8;
            font-weight: 500;
            border: none;
            padding: 0 16px;
            transition: all 0.2s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #f1f5f9;
            background-color: rgba(255, 255, 255, 0.05);
        }

        .stTabs [aria-selected="true"] {
            background-color: #6366f1 !important;
            color: white !important;
            font-weight: 600 !important;
        }
        
        /* Expanders */
        .stExpander {
            background-color: rgba(30, 41, 59, 0.15) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px !important;
            margin-bottom: 0.75rem !important;
        }

        /* Compact Scene Control Buttons */
        .scene-control-btn-container div.stButton > button {
            background: rgba(30, 41, 59, 0.6) !important;
            color: #f1f5f9 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 0.3rem 0.5rem !important;
            font-size: 0.85rem !important;
            box-shadow: none !important;
            border-radius: 6px !important;
            width: 100% !important;
            min-width: 0px !important;
        }
        .scene-control-btn-container div.stButton > button:hover {
            background: rgba(99, 102, 241, 0.25) !important;
            border-color: rgba(99, 102, 241, 0.5) !important;
            color: white !important;
            transform: none !important;
        }
    </style>
    """
