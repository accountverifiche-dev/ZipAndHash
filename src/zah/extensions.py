from typing import Set


__all__ = ["allowed_ext"]


allowed_ext: Set[str] = {
    # Text & Documents
    ".txt", ".csv", ".tsv", ".md", ".rtf",
    ".pdf", ".doc", ".docx", ".odt",
    ".xls", ".xlsx", ".ods",
    ".ppt", ".pptx", ".odp",

    # Configurations
    ".json", ".yaml", ".yml", ".ini", ".toml", ".conf", ".cfg", ".env",

    # Images
    ".png", ".jpg", ".jpeg", ".svg", ".gif", ".bmp", ".tiff", ".webp", ".ico",

    # Audio
    ".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".wma", ".amr",

    # Video
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".mpg", ".mpeg",

    # Archives
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",

    # Fonts
    ".ttf", ".otf", ".woff", ".woff2",

    # XML
    ".xml", ".xsd", ".dtd",

    # Web
    ".html", ".htm", ".css",

    # Python
    ".py", ".pyi", ".pyx", ".pxd", ".pxi",

    # C / C++
    ".c", ".h", ".cpp", ".hpp", ".cc", ".hh", ".cxx", ".hxx",

    # Javascript / Typescript / Web Frameworks
    ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".vue", ".svelte", ".astro",

    # C# / .NET
    ".cs", ".csx", ".cshtml",

    # Other programming languages
    ".java", ".kt", ".kts", ".go", ".rs", ".swift", ".rb", ".php", ".phtml",

    # Shell / Script
    ".sh", ".bash", ".zsh", ".bat", ".cmd",
    ".ps1", ".psm1", ".psd1",

    # DB / Data formats
    ".sql", ".db", ".sqlite", ".geojson", ".parquet", ".avro",
}