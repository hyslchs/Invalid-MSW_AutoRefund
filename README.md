# 7/24 MSW 平台更新，現台港澳服已無法主動退款，此腳本已失效
# MSW 自動退款操作手冊 
(最後更新 2025/07/24)

原始碼：https://github.com/hyslchs/MSW_AutoRufund?tab=readme-ov-file

## 注意事項
- MSW 官網有時會出現彈出式廣告視窗，可能會導致程式無法正常運行，若出現請在程式開啟瀏覽器後手動將彈出式式窗關閉
- 與買家索取唯一代碼時，請注意含有大寫`I`或是小寫`l`的代碼，遊戲中兩個字母非常容易誤認，可能導致誤殺的情況發生。
可以從執行狀態檢視是否有出現查無訂單的代碼，執行結束後再針對這些代碼複檢一遍。
- `Cookie.pkl` 過一段時間後可能會失效，建議一段時間沒執行就手動登入一次並重新儲存 Cookie。
- **絕對不要隨意將 `Cookie.pkl` 傳送給任何人**


---

若有任何 bug、操作疑問可透過以下管道聯絡：
- mail：hyslchs@gmail.com
- Discord：hyslchs

## 操作步驟

:::success
執行過程中若想終止執行，請直接關閉由程式啟動的瀏覽器
:::

### 一、取得並儲存 Cookie
![image](https://hackmd.io/_uploads/B1U8v0h8xl.png)

點擊「1.開啟瀏覽器登入」後，會自動開啟一個 chrome 瀏覽器，並進入 MSW 的官網首頁

![image](https://hackmd.io/_uploads/rJJhDR28xg.png)

請手動點擊「登入」

![image](https://hackmd.io/_uploads/SyGRvRhIxe.png)

請透過左邊欄位手動輸入帳號密碼，右邊的第三方登入通常會阻擋「受自動控制的瀏覽器」，因此無法透過第三方登入 MSW 官網。

![image](https://hackmd.io/_uploads/ry5OuC3Llx.png)
![image](https://hackmd.io/_uploads/BkR9_ChIxg.png)

確認登入成功後，回到主程式點選「2.儲存Cookie並關閉」

![image](https://hackmd.io/_uploads/SkyYUJT8ee.png)

便會在同一路徑下生成 `cookies.pkl` 的檔案

:::danger
請注意，任何人都可以透過 `cookies.pkl` 隨意登入你的帳號，
因此絕對不要將這份檔案傳送給任何人
:::


---

### 二、取得並儲存 Cookie

**在執行之前，請先檢查同一路徑下是否有 `buyer.txt` 這個文件，如果沒有就自己建立一個**

![image](https://hackmd.io/_uploads/BJbSqAnIel.png)

![image](https://hackmd.io/_uploads/B1R950h8gx.png)

此處的頁數與日期與你的明細頁面相同，請依照自身情況調整

![image](https://hackmd.io/_uploads/B1s7jAnLxg.png)

在 `buyer.txt` 中，輸入你的買家的帳號唯一代碼 (#後面五位英數字的那個)
並請注意不要輸入到 `#` 符號

`buyer.txt` 建立完成並儲存後，即可按下「開始抓取與標記」，此時便會開啟一個 chrome 瀏覽器，開始檢索所有的帳號唯一代碼、與你設定頁數的訂單明細。

:::warning
執行過程中請不要進行任何的交易行為，否則可能會導致抓取結果出現預期外的錯誤
:::

![image](https://hackmd.io/_uploads/rybZhCn8xg.png)

可以在執行狀態中檢視每一個步驟的查詢狀況

![image](https://hackmd.io/_uploads/SkvnUyTLlx.png)


此步驟完成後，會看到同一路徑下多出很多文字文件，此處請開啟 `marked_order_id.txt` 即可

![image](https://hackmd.io/_uploads/S1kvaRh8ge.png)

文件中含有 `※` 標記的即為「正常買家」的訂單編號，可從此處自行檢查一次抓取過程中是否有缺漏、誤殺等情形 
**若無 `※` 標記的訂單會在下一步驟自動執行退款**

---
### 三、執行自動退款

:::warning
退款為不可逆的行為，點擊開始退款之前請先檢查 `marked_order_id.txt` 內是否已經正確標記「正常買家的訂單」
如果不慎誤觸也請直接關閉「由程式啟動的瀏覽器」即可停止執行
:::

![image](https://hackmd.io/_uploads/SkfjJy6Ile.png)

執行過程可在執行狀態看到目前進度、與執行狀況
(正確執行的話應出現 `✅ 已點擊『退款』按鈕` 此處暫無範例圖示)


如果出現以下錯誤：
- `處理訂單 xxxxxxxx 時發生超時錯誤`，代表：
    - 該頁面找不到退款按鈕，可能已被退款完成
- `訂單 xxxxxxxx 無法退款（彈出『失敗』視窗）`，代表：
    - 買家是韓服帳號，賣家無法主動退款
    - 售出已超過 30 天，無法退款

---
## 運作原理
1. 使用者手動登入帳號後，透過程式讀取 cookie 並儲存在本地端，接著即可使用這份 `cookie.pkl` 進行自動登入
2. 讀取 buyer.txt 後，依序抓取「正常買家」的訂單編號
3. 使用者設定欲抓取的明細頁數，抓取該範圍內的「所有訂單編號」
4. 比對「所有訂單編號」與「正常買家」的訂單編號，以 `※` 標記出「正常買家」的訂單編號
5. 無標記的訂單編號則為「非正常買家」的訂單

> MSW 明細網頁的網址如下(範例)
> `https://maplestoryworlds.nexon.com/zh-tw/coin/history?type=earning&page=1&startDate=2025-06-22&endDate=2025-07-22&searchCategory=O&searchKeyword=12345678`
>
>其中
> `page` 就是檢索的頁數
> `startDate` 與 `endDate` 為檢索日期範圍
> 
> `searchCategory=O` 為透過「訂單編號」進行檢索
> `searchCategory=B` 為透過「購買者唯一代碼」進行檢索
> 
> `searchKeyword=` 即為搜索關鍵字

**只要直接在網址改變這些欄位的資訊，就可以不用透過前端直接進行檢索**

## 各文字文件內容說明
- `buyer.txt` 此為使用者唯一須編輯的檔案，用以儲存買家的帳號唯一代碼
- `buyer's_order_id.txt` 此為程式自動產生，用以記錄正常買家的訂單編號
- `all_order_id.txt` 此為程式自動產生，用以紀錄指定頁數範圍中的所有訂單編號
- `mark_order_id.txt` 此為程式自動產生，用以標記全部訂單與正常買家的訂單
- `refund_log.txt` 此為程式自動產生，用以記錄執行狀態與過程

## 免責聲明
> 本程式僅為技術研究與反制用途之開發，不保證其使用完全符合 Nexon《MapleStory Worlds》平台之使用規範，旨在「用魔法對付魔法」。
> 
> 若因使用本程式導致 Nexon 採取停權、帳號限制或其他懲處措施，本人恕不負責，風險請使用者自負。

