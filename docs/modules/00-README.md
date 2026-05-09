# Пользователи и группы (Users & Groups)

**Модуль ServiceNow:** Users (`sys_user`), Groups (`sys_user_group`), Group Members (`sys_user_grmember`)

## Назначение
Поиск пользователей и групп, получение состава групп, проверка ролей.

## Что умеет MCP-инструмент

| Инструмент | Описание |
|------------|----------|
| `user_info` | Поиск пользователя по email или имени |
| `group_members` | Состав группы: участники, количество |

## Примеры использования

```
> Найди пользователя vasily.pupkin@company.com
> Кто входит в группу DBA Team?
> Покажи всех участников Service Desk
```

## Ключевые поля

- `email` — адрес пользователя
- `group` → `user` — связка группа-участник
- `sys_user` / `sys_user_group` / `sys_user_grmember`

---

*Автор: Vlady | Лицензия: AGPL-3.0 | 2026*

---

# 📋 Сводка всех MCP-модулей

| # | Модуль | Инструментов | Таблица ServiceNow |
|---|--------|:-----------:|-------------------|
| 01 | Incident Management | 5 | `incident` |
| 02 | Change Management | 3 | `change_request` |
| 03 | Problem Management | 3 | `problem` |
| 04 | Service Catalog | 4 | `sc_cat_item`, `sc_request`, `sc_req_item` |
| 05 | CMDB | 3 | `cmdb_ci`, `cmdb_rel_ci` |
| 06 | Knowledge Base | 1 | `kb_knowledge` |
| 07 | Reporting & Analytics | 1 (4 метрики) | `task_sla`, `incident` |
| 08 | Workflows | 1 | `wf_workflow_version` |
| 09 | Integrations | 1 | `sys_rest_message` |
| 10 | Business Rules | 1 | `sys_script` |
| 11 | Users & Groups | 2 | `sys_user`, `sys_user_group` |

**Всего: 26 инструментов поверх 12 таблиц ServiceNow.**
