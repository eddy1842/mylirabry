# My-calibre-webserver-docker

[![Docker Pulls](https://img.shields.io/docker/pulls/oldiy/my-calibre-webserver-docker.svg)][dockerhub] 

[dockerhub]: https://hub.docker.com/r/oldiy/my-calibre-webserver-docker

---

執行命令

`docker run -d --name calibre-webserver -p 8000:8000 -v <本機data目錄>:/data oldiy/my-calibre-webserver-docker`

---

+ [ [群暉安裝教程](https://odcn.top/2019/02/26/2734/) ]

+ [ [Blog](https://odcn.top) ]

+ 加入我的Telegram討論組 [[Join](https://t.me/joinchat/H3IoGkcnW6BGo51EJ9Kw5g)]

- Docker默認為單機版tag：latest，如果需要多用戶版可以使用tag：multi-user，其他問題請參考[安裝文檔](https://github.com/oldiy/my-calibre-webserver/blob/master/docs/INSTALL.zh_CN.md)進行修改，如果需要Kindel推送，需要設置smtp後重啟容器才可以使用！

- 更新支持github登錄

- 演示地址 [[ 奇藝書屋 ](https://www.talebook.org)]

- 這是一個基於Calibre的簡單的圖書管理系統，支持**在線閱讀**。主要特點是：
- 由於Calibre自帶的網頁太醜太難用，於是獨立編寫了一個。
- 為了網友們更方便使用，開發了多用戶功能，支持~~豆瓣~~（已廢棄）、QQ和微博登錄。
- 藉助[Readium.js](https://github.com/readium/readium-js-viewer) 庫，支持了網頁在線閱讀電子書。
- 支持從百度百科、豆瓣搜索並導入書籍基礎信息。

部署比較簡答，可以參考[安裝文檔](https://github.com/oldiy/my-calibre-webserver/blob/master/docs/INSTALL.zh_CN.md)

已添加Docker一鍵部署，可以查看[my-calibre-webserver-docker](https://hub.docker.com/r/oldiy/my-calibre-webserver-docker)

---

![](https://odcn.top/wp-content/uploads/2019/02/6-7.jpg)

---

![](https://odcn.top/wp-content/uploads/2018/11/%E9%BB%91%E5%88%BA%E7%8C%AC%E6%A8%AA150.png)
