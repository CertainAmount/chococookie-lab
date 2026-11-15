# 최소 ELF64 헤더만 있는 파일을 만든다. e_machine=183(AArch64).
# 실행 코드는 없다. x86_64 커널이 "이 CPU용이 아니다"라고 거부하는지만 본다.
import os
import struct

ident = b'\x7fELF' + bytes([2, 1, 1, 0]) + b'\0' * 8   # 64비트, 리틀엔디언, 버전 1
hdr = ident + struct.pack(
    '<HHIQQQIHHHHHH',
    2,          # e_type: ET_EXEC
    183,        # e_machine: EM_AARCH64
    1,          # e_version
    0x400078,   # e_entry
    64,         # e_phoff
    0,          # e_shoff
    0,          # e_flags
    64,         # e_ehsize
    56,         # e_phentsize
    0,          # e_phnum
    64,         # e_shentsize
    0,          # e_shnum
    0,          # e_shstrndx
)
with open('hello-arm64', 'wb') as f:
    f.write(hdr)
os.chmod('hello-arm64', 0o755)
