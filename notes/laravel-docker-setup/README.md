---
title: "Laravel Docker 설정: 첫날은 Sail, 운영과 같은 구조는 nginx+php-fpm 직접 compose"
checked: 2026-11-16
article_url: https://jjeongil.tistory.com/3072
---

# laravel/laravel 13.x·12.x composer.json 대조

Laravel 13 스켈레톤의 `require-dev`에서 `laravel/sail`이 빠졌는지, 12.x와 무엇이 다른지 저장소 원본 파일로 확인한 기록이다.

## 파일

| 파일 | 내용 |
|---|---|
| `composer-json-compare.csv` | 브랜치별 기준 커밋(SHA 앞 12자리, 커밋 시각 UTC)과 `php`, `laravel/framework`, `require-dev`의 `laravel/sail` 값. 13.x의 sail 칸이 비어 있는 것은 키가 없다는 뜻(스크립트 출력 `None`) |
| `compare2.log` | 두 브랜치의 composer.json을 받아 값을 뽑은 명령과 출력 원문 |
| `fields.py` | composer.json에서 세 값을 출력하는 스크립트 |
| `sha.log` | 조회 시점의 브랜치 최신 커밋 SHA와 커밋 시각 |

## 수집 방법과 기준일

- 기준일: 2026-11-16.
- `https://raw.githubusercontent.com/laravel/laravel/{13.x,12.x}/composer.json`을 `curl`로 받고 `python3 fields.py <파일>`로 `require.php`, `require.laravel/framework`, `require-dev.laravel/sail`을 출력했다.
- 기준 커밋은 GitHub API `repos/laravel/laravel/commits/{브랜치}` 응답의 `sha`와 `commit.committer.date`다.

## 출처

- laravel/laravel 저장소 — https://github.com/laravel/laravel (13.x, 12.x 브랜치)
- Laravel Sail 13.x 문서 — https://laravel.com/docs/13.x/sail (설치 순서 `composer require laravel/sail --dev` → `php artisan sail:install`)
- Laravel 13.x 설치 문서 — https://laravel.com/docs/13.x/installation

## 한계

- 브랜치 최신 파일을 본 것이다. `laravel new`나 `composer create-project`로 13.x 프로젝트를 만든 결과와 같다고 실행으로 확인하지는 않았다.
- 브랜치는 계속 커밋되므로 이후 값은 바뀔 수 있다. 위 SHA가 비교 기준점이다.
