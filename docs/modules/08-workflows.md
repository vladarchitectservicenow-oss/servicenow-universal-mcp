# Рабочие процессы (Workflows & Flow Designer)

**Модуль ServiceNow:** Workflow Versions (`wf_workflow_version`), Flows

## Назначение
Просмотр и аудит автоматизированных рабочих процессов (workflows, flows), опубликованных в системе.

## Что умеет MCP-инструмент

| Инструмент | Описание |
|------------|----------|
| `workflow_list` | Список опубликованных workflows с поиском по названию |

## Примеры использования

```
> Покажи все опубликованные workflows
> Найди workflow для процесса онбординга
> Сколько у нас активных flows связано с инцидентами?
```

## Ключевые поля

- `wf_workflow_version` — версии рабочих процессов
- `published=true` — только опубликованные
- 6 workflows на PDI (май 2026)
- ServiceNow Australia: Workflow Studio объединяет Flow Designer + Playbooks + Decision Tables

---

*Автор: Vlady | Лицензия: AGPL-3.0 | 2026*
