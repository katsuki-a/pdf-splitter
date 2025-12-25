import re

def sanitize_filename(filename: str) -> str:
    """
    ファイル名として使用できない文字を置換する。
    
    Args:
        filename (str): 元のファイル名
        
    Returns:
        str: サニタイズされたファイル名
    """
    # Windows/Unix系でファイル名に使えない文字をアンダースコアに置換
    return re.sub(r'[\\/*?:"<>|]', "_", filename)
