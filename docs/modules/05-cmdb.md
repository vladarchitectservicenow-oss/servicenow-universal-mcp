# CMDB (Configuration Management Database)

**Модуль ServiceNow:** Configuration Items (`cmdb_ci`), Relationships (`cmdb_rel_ci`)

## Назначение
Учёт и управление конфигурационными единицами (CI): серверы, приложения, базы данных, сеть. Отслеживание зависимостей между ними.

## Что умеет MCP-инструмент

| Инструмент | Описание |
|------------|----------|
| `cmdb_search` | Поиск CI: название, класс, окружение |
| `cmdb_relationships` | Зависимости: что зависит от CI и от чего зависит он |
| `cmdb_health` | Здоровье CMDB: дубликаты, сироты, устаревшие |

## Примеры использования

```
> Найди все серверы в Production на Windows Server 2019
> Какие приложения зависят от PROD-DB-01?
> Покажи зависимости для SAP-кластера
> Дай сводку здоровья CMDB
```

## Ключевые поля

- `name` — название CI
- `sys_class_name` — класс (Server, Application, Database, Network Gear...)
- `environment` — Production, Test, Development, Staging
- `cmdb_rel_ci` — parent → child отношения

---

*Автор: Vlady | Лицензия: AGPL-3.0 | 2026*
