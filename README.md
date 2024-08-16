# AIの力を借りてコピペツールを作ってみた
## 推奨環境
・PC（たぶん）（スマホはムリ）

## 主な仕様
・日本語、ASCII対応  
・改行回数指定可能  
・常に実行ファイル最前面表示可能  
・貼り付け秒数間隔指定可能  
・自動Enterツールとしても使用可能  
・単語帳に複数登録しているとランダムに出力される  

## つかいかた
1. [CopyPasteApp_v2.exe](https://github.com/Siyu062/copy_paste_app/blob/main/CopyPasteApp_v2.exe) から「Download raw file」（「View raw」でも可）をクリックしてダウンロード
2. ダウンロードしたCopyPasteApp_v2.exeを実行  
2.1. （Windowsの場合）Microsoft Defender SmartScreenでブロックされたら「詳細情報」→「実行」から始められるよ  

## ごちゅうい
・ 設定をいじると「config.json」、単語を登録すると「words.json」がCopyPasteApp_v2.exeと同じディレクトリに生成されます。消すと設定や登録した単語が吹き飛びますが動作に支障はありません。  
　　　（例）ファイル１にCopyPasteApp_v2.exeを置く  
　　　　　　ファイル１  
　　　　　　└ CopyPasteApp_v2.exe  
              
　　　　　　CopyPasteApp_v2.exeを実行して単語登録と設定変更を行った  
　　　　　　ファイル１  
　　　　　　├ CopyPasteApp_v2.exe  
　　　　　　├ words.json  
　　　　　　└ config.json
            
