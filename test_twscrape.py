import os
import asyncio
from dotenv import load_dotenv
from twscrape import API, gather

async def test_x_scraper():
    # 載入 .env 檔案
    load_dotenv()
    username = os.getenv("X_USERNAME")
    password = os.getenv("X_PASSWORD")
    email = os.getenv("X_EMAIL")
    email_password = os.getenv("X_EMAIL_PASSWORD")
    
    if not username or "你的x登錄用戶名" in username:
        print("❌ 未在 .env 找到有效的 X_USERNAME。請確認檔案已保存且正確填寫。")
        return

    # 初始化 twscrape API
    api = API()
    
    print(f"📥 正在將帳號 {username} 加入爬蟲連線池...")
    # Add account (it automatically ignores if the account already exists in db)
    await api.pool.add_account(username, password, email, email_password)
    
    print("🔐 正在嘗試登錄 (這可能會花費 10~30 秒，包含驗證流程)...")
    await api.pool.login_all()
    
    print("\n✅ 登錄嘗試結束，正在獲取您的帳號資訊以驗證登錄狀態...")
    try:
        me = await api.user_by_login(username)
        if not me:
            print("❌ 無法獲取帳號資訊，可能是登錄失敗或帳號異常 (如需手機驗證碼鎖定)。")
            return
            
        print(f"👤 您已成功登錄！ 用戶名: @{me.username} | 註冊名稱: {me.displayname} | 粉絲數: {me.followersCount}")
        
        print(f"\n🔍 正在獲取您 (@{me.username}) 的關注列表 (本次測試最多抓取 5 個)...")
        # 抓取關注的對象
        following = await gather(api.following(me.id, limit=5))
        
        if not following:
            print("⚠️ 您目前沒有關注任何人，或抓取為空。")
            return
            
        print(f"✅ 成功抓取到 {len(following)} 個關注對象：")
        for i, u in enumerate(following):
            desc_preview = u.rawDescription[:20].replace('\n', ' ') if u.rawDescription else "無自介"
            print(f"  {i+1}. @{u.username} - {desc_preview}...")
            
        # 測試抓取其中一位博主最近的推文
        first_target = following[0]
        print(f"\n📝 正在嘗試獲取 @{first_target.username} 最近的推文 (最多 3 條)...")
        tweets = await gather(api.user_tweets(first_target.id, limit=3))
        
        if not tweets:
            print("⚠️ 該博主最近沒有發推文。")
        else:
            for t in tweets:
                # 解決部分終端編碼問題
                text_preview = t.rawContent[:50].replace('\n', ' ')
                print(f"   💬 [{t.date.strftime('%Y-%m-%d %H:%M')}] {text_preview}...")
            
        print("\n🎉 X 爬蟲完整流程 (登錄 -> 查關注 -> 獲取推文) 測試成功！")
        
    except Exception as e:
        print(f"\n❌ 操作過程中發生錯誤：{e}")

if __name__ == "__main__":
    asyncio.run(test_x_scraper())
