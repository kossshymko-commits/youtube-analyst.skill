# Инструменты и запасные варианты

Скилл работает с любым набором подключённых коннекторов. Для каждой задачи пробуй варианты сверху вниз и бери первый, который сработал. Если коннекторы не загружены, сначала найди их через поиск инструментов (tool_search) по ключевым словам: "vidiq", "nexlev", "youtube".

## Данные канала
1. vidIQ: `vidiq_channel_stats`, `vidiq_channel_videos`, `vidiq_channel_performance_trends`
2. NexLev: `youtube_channel_about`, `youtube_channel_videos`, `youtube_channel_shorts`, `get_channel_analytics`, `check_channel_monetization`
3. Запасной вариант: веб-поиск + web_fetch страницы канала (данные будут неполными — предупреди)

Если это **собственный канал пользователя** и он авторизован: `vidiq_channel_analytics` / NexLev `get_my_channel_analytics`, `get_my_audience_retention`, `get_my_traffic_sources` — это реальные CTR, удержание и источники трафика. Всегда предпочитай их публичным цифрам.

## Залетевшие ролики (outliers)
1. vidIQ: `vidiq_outliers` (по нише/ключу), `vidiq_trending_videos`
2. NexLev: `youtube_channel_outliers` (по каналу), `search_viral_videos_small_channels`, `faceless_outliers_videos`
3. Запасной вариант: посчитай сам по спискам видео (методика в `outliers.md`)

## Конкуренты и похожие каналы
1. vidIQ: `vidiq_similar_channels`, `vidiq_channel_search`
2. NexLev: `get_similar_channels` (асинхронный — опроси `get_similar_channels_status`), `search_niche_finder_channels`, `get_niche_overview`

## Обложки
1. Увидеть картинку: возьми URL обложки из данных видео (обычно `https://i.ytimg.com/vi/<VIDEO_ID>/hqdefault.jpg` или maxresdefault) и открой через web_fetch, если URL уже встречался в результатах. Если картинку увидеть не удалось, используй `image_search` по названию видео.
2. Оценка: vidIQ `vidiq_score_thumbnail`
3. Похожие обложки: vidIQ `vidiq_similar_thumbnails`, NexLev `get_similar_thumbnails`
4. Генерация (только если пользователь просит): vidIQ `vidiq_generate_thumbnail`, NexLev `generate_thumbnail`

## Заголовки
- Оценка: vidIQ `vidiq_score_title`
- Генерация вариантов для сравнения: vidIQ `vidiq_generate_titles` (свои варианты всё равно пиши сам по паттернам ниши)
- Спрос: vidIQ `vidiq_keyword_research`

## Транскрипты и содержание
1. vidIQ `vidiq_video_transcript`, NexLev `get_video_transcript` / `get_bulk_video_transcripts` (до 10 сразу)
2. Понять визуал и подачу: NexLev `watch_youtube_video_and_ask`, vidIQ `vidiq_video_watch`

## Комментарии и аудитория
- vidIQ `vidiq_comment_insights` (по нише), `vidiq_video_comments`
- Ищи: повторяющиеся вопросы, просьбы «сделай видео про…», возражения, жалобы. Это готовые темы.

## Тренды
- vidIQ `vidiq_trending_videos`, `vidiq_trend_categories`
- NexLev `search_youtube_suggested_videos`, `latest_discovered_faceless_niches`

## Деньги (если спрашивают)
- NexLev `get_video_rpm`, `get_geography_revenue`; vidIQ `vidiq_video_earnings_estimate`

## Правила
- Не вызывай платные/генеративные инструменты (генерация обложек, видео, озвучки) без прямой просьбы пользователя — они тратят кредиты.
- Если инструмент вернул ошибку авторизации или лимит — переходи к следующему варианту, в ответе упомяни одной строкой.
- Не меняй ничего на канале пользователя (`vidiq_update_video` и подобное) без явного подтверждения.
