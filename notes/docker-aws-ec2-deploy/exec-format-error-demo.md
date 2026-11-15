# x86에서 arm64 실행 파일을 실행하면 (2026-11-15)

- 목적: Mac(Apple Silicon)에서 플랫폼 지정 없이 만든 arm64 이미지가 x86 EC2에서 `exec format error`로 죽는 원리를 보여 준다. Docker 자체를 재현한 것은 아니다.
- 방법: x86_64 리눅스에서 `/bin/true`를 복사하고 ELF 헤더의 기계 종류(e_machine, 오프셋 18)만 aarch64(0xB7)로 바꾼 뒤 실행했다. 진짜 arm64 바이너리가 아니라 「다른 아키텍처용」이라고 표시된 파일이다.
- 결과: 커널이 형식을 거부해 `cannot execute binary file: Exec format error`. 출력은 `exec-format-error-demo.txt`.
