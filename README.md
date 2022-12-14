## Анализатор логов

Скрипт обрабатывает лог файл в директории ```./log``` с самой свежей датой в имени файла. 

Допустимые файлы: 
* nginx-access-ui.log-20170630
* nginx-access-ui.log-20170630.gz

Если два файла c одинаковой датой, но в разных форматах, то выбирается текстовый.

Отчет генерируется в директории ```./reports```. Формат имени файла с отчётом ```report-2017.06.30.html```. 
При первом запуске скрипта генерируется файл с настройками по умолчанию ```./config.json```.
При необходимости его можно отредактировать и перенести в другое место. 
Логи о процессе выполнения скрипта по умолчанию выводятся на стандартный ввод вывод,
но могут и записываться в файл, имя которого задаётся в настройках переменной ```"LOG_FILE"```.

### запуск скрипта
```shell
python.exe log_analyzer.py  --config /path/to/config
```

### запуск тестов
```shell
python -m unittest .\test_log_analyzer.py
```
