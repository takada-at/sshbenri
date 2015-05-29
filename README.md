sshbenri
========

多重SSH接続を便利に使用するためのスクリプトです。

## インストール
```
pip install sshbenri
```

## 使い方
 複数のホストを渡すと、sshコマンドを作成して実行します。
```
$ sshbenri host1 host2 host3
```

 実行されるコマンド

```
$ ssh -t -A host1 ssh -t -A host2 ssh -t -A host3
```

### オプションが必要な場合

```
$ sshbenri host1 '-i ~/otherkey host2' host3
```

実行されるコマンド

```
$ ssh -t -A host1 ssh -t -A -i \~/otherkey host2 ssh -t -A host3
```

### すべてに12345ポートを通す

```
$ sshbenri host1 host2 host3 -p 12345
```

 実行されるコマンド

```
$ ssh -t -A -L12345:localhost:12345 host1 ssh -t -A -L12345:localhost:12345 host2 ssh -t -A -L12345:localhost:12345 host3
```

### echo $HOME && echo \$HOMEを実行

```
$ sshbenri host1 host2 -e 'echo $HOME && echo \$HOME'
```

 実行されるコマンド

```
$ ssh -t -A host1 ssh -t -A host2 'echo \$HOME \&\& echo \\\$HOME \&\& date +"%Y-%m-%d"'
```

## 設定ファイル
home直下に.sshbenri.py というファイルがあれば、それを読みます。

たとえば以下の設定が登録されていれば、

    "app1": {
        "host": ["host1", "user@host2"]
    },

下のコマンドが

```
$ sshbenri app1
```

以下のように展開されます。

```
$ ssh -t -A host1 ssh -t -A user@host2
```


## rsync
rsyncbenriも開発しました

```
$ rsyncbenri ./path host0 host1:/path
```

実行されるコマンド
```
$ rsync -rv -e 'ssh -t -A host0 ssh' ./path host1:'/path'
```
