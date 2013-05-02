sshbenri
========

多重SSH接続を便利に使用するためのスクリプトです。

## インストール
    git clone https://github.com/takada-at/sshbenri.git
    cd sshbenri
    python setup.py install

## 使い方

    sshbenri 'host1, host2, host3'

→ 実行されるコマンド
    ssh -t -A host1 ssh -t -A host2 ssh -t -A host3

### オプションが必要な場合

    sshbenri 'host1, -i ~/otherkey host2, host3'

→ 実行されるコマンド

    ssh -t -A host1 ssh -t -A -i \~/otherkey host2 ssh -t -A host3

### すべてに12345ポートを通す

    sshbenri 'host1, host2, host3' -p 12345

→ 実行されるコマンド

    ssh -t -A -L12345:localhost:12345 host1 ssh -t -A -L12345:localhost:12345 host2 ssh -t -A -L12345:localhost:12345 host3

### echo $HOME && \$HOMEを実行

    sshbenri 'host1, host2, host3' -e 'echo $HOME && \$HOME'

→ 実行されるコマンド

    ssh -t -A host1 ssh -t -A host2 ssh -t -A host3 echo \\\\\\\$HOME \\\\\\\&\\\\\\\& \\\\\\\\\\\\\\\$HOME

## 設定ファイル
home直下に.sshbenri.py というファイルがあれば、それを読みます。

たとえば以下の設定が登録されていれば、

    "app1": {
        "host": "host1, user@host2"
    },

下のコマンドが

    sshbenri app1

以下のように展開されます。

    ssh -t -A host1 ssh -t -A user@host2
