# ChangeLog
## 0.0.7
*New*
 - sshbenriのコマンド実行も複数サーバー上で実行できるようにした
 
## 0.0.6

*New*
 - python3に対応
 - 設定ファイルの書き方を修正(後方互換もあり)
 - rsync先として中継サーバーも指定できるようにした 

設定の書き方について。

今までは以下のようになっていた。

```
host = "host1,host2"
```

これは不恰好なので以下のように書けるようにする。
```
host = ["host1", "host2"]
```

rsync先の指定方法について。

以下のように書く。

```
hosts = {
    "app1": {
        "host": ["host1", "user@host2"],
        "target": ["host1", "user@host2"],
    },
```
