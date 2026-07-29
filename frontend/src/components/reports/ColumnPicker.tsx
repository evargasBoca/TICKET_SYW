import { useState } from 'react'
import { Button, Checkbox, Popover } from 'antd'
import { SettingOutlined, HolderOutlined } from '@ant-design/icons'
import { DragDropContext, Droppable, Draggable, type DropResult } from '@hello-pangea/dnd'
import { palette } from '../../theme'

export interface ColumnDef {
  key: string
  title: string
}

interface Props {
  /** Todas las columnas (visibles y ocultas), en el orden actual. */
  columns: ColumnDef[]
  visibility: Record<string, boolean>
  onReorder: (orderedKeys: string[]) => void
  onToggle: (key: string, visible: boolean) => void
}

/** Mostrar/ocultar/reordenar columnas del reporte (spec 034, US3) — Popover + Checkbox +
 * @hello-pangea/dnd, sin dependencias nuevas (research.md Decisión 5). */
export default function ColumnPicker({ columns, visibility, onReorder, onToggle }: Props) {
  const [open, setOpen] = useState(false)

  const handleDragEnd = (result: DropResult) => {
    if (!result.destination) return
    const keys = columns.map(c => c.key)
    const [moved] = keys.splice(result.source.index, 1)
    keys.splice(result.destination.index, 0, moved)
    onReorder(keys)
  }

  return (
    <Popover
      trigger="click"
      open={open}
      onOpenChange={setOpen}
      placement="bottomRight"
      content={
        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="report-columns">
            {(provided) => (
              <div ref={provided.innerRef} {...provided.droppableProps} style={{ width: 240 }}>
                {columns.map((col, index) => (
                  <Draggable key={col.key} draggableId={col.key} index={index}>
                    {(dragProvided) => (
                      <div
                        ref={dragProvided.innerRef}
                        {...dragProvided.draggableProps}
                        {...dragProvided.dragHandleProps}
                        style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 2px', ...dragProvided.draggableProps.style }}
                      >
                        <HolderOutlined style={{ color: palette.slate400 }} />
                        <Checkbox
                          checked={visibility[col.key] ?? true}
                          onChange={(e) => onToggle(col.key, e.target.checked)}
                        >
                          {col.title}
                        </Checkbox>
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>
      }
    >
      <Button icon={<SettingOutlined />}>Columnas</Button>
    </Popover>
  )
}
