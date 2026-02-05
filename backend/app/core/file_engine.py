
class FileEngine():
    def __init__(self, workspace: str = Depends(settings.TEMP_DIR)):
        self.workspace = workspace
        
    def store_file(self, file: UploadFile) -> str:
        """
        存储文件到工作空间
        """
        pass
    
    def split_file(self, file_path: str) -> List[str]:
        """
        分割文件为多个段落
        """
        pass
