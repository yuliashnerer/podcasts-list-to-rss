docker build . -t podcasts-list-to-rss --build-arg TELEGRAM_APP_ID=${TELEGRAM_APP_ID} --build-arg TELEGRAM_APP_HASH=${TELEGRAM_APP_HASH} --build-arg TELEGRAM_PUBLIC_CHANNEL_NAME=${TELEGRAM_PUBLIC_CHANNEL_NAME}

docker run podcasts-list-to-rss