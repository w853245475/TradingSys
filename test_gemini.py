import os
from dotenv import load_dotenv
from google import genai

def test_gemini_api():
    # 載入 .env 檔案
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ 錯誤：找不到有效的 GEMINI_API_KEY，請確認 .env 檔案已正確填寫！")
        return

    print("🔑 已讀取到 API Key，正在嘗試連線 Google Gemini 伺服器...")
    
    try:
        # 初始化 GenAI 客戶端
        client = genai.Client(api_key=api_key)
        
        # 嘗試發送一個簡單的測試對話
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='請用繁體中文回覆這句話："API 連線測試成功！這是來自 Gemini 的問候。"'
        )
        
        print("\n✅ API 測試成功！以下是 AI 的回覆：")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        
    except Exception as e:
        print("\n❌ API 測試失敗。錯誤訊息：", e)
        print("\n正在列出此 API Key 支援的模型清單...")
        try:
            for m in client.models.list():
                print(m.name)
        except Exception as e2:
            print("獲取模型列表失敗：", e2)

if __name__ == "__main__":
    test_gemini_api()
