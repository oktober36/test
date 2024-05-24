# Python интерфейс к файлу hosts

Модуль и класс для удобных манипуляций с [файлом hosts](https://manpages.ubuntu.com/manpages/jammy/man5/hosts.5.html) в интересах ПО кластера.

<h2> Структура </h2>

Модуль состоит из 2 классов для взаимодействия  
  
NTSGHosts,
NTSGEntry  
  
Для взаимодействия с файлом можно пользоваться только NTSGHosts

<h2> Использование </h2>

NTSGHosts имеет многие методы класса Hosts из [python_hosts](https://pypi.org/project/python-hosts/),
за некоторыми исключениями  

```python
hosts = NTSGHosts("/path/to/hosts")
```

`NTSGHosts.add` добавление записи в блок. Аргументом может быть как экземпляр NTSGEntry, так и аргументы
для его создания

```python
hosts.add(("1.1.1.1", "1"))

hosts.add(NTSGEntry("1.1.1.1", "1"))

ne = NTSGEntry("1.1.1.1", "1")
hosts.add(ne)
```
 
В следующих методах есть необязательный аргумент include_outer_entries, при указании его True, действия (поиск, удаление)
будут производиться не только с записями в блоке, но и со всеми остальными


`NTSGHosts.remove` удаление записи по имени


`NTSGHosts.clear` удаление всех записей



`NTSGHosts.get_name_by_address` поиск имени по адресу, выводит список адресов

`NTSGHosts.get_address_by_name`, `NTSGHosts.get_address_by_regexp`  поиск адресов по имени

`NTSGHosts.contains` проверка существования записи по имени или адресу, так же можно использовать конструкцию
`in` для проверки по имени

```python
hosts.contains(name="1")

hosts.contains(address="1.1.1.1")

"1" in hosts
```

