<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotesStore } from '@/stores/notes'
import { useEditorStore } from '@/stores/editor'
import { useUiStore } from '@/stores/ui'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import Highlight from '@tiptap/extension-highlight'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import Table from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import Link from '@tiptap/extension-link'
import Underline from '@tiptap/extension-underline'
import Typography from '@tiptap/extension-typography'
import CharacterCount from '@tiptap/extension-character-count'
import UiButton from '@/components/ui/UiButton.vue'

const route = useRoute()
const router = useRouter()
const notesStore = useNotesStore()
const editorStore = useEditorStore()
const ui = useUiStore()

const notebookId = route.params.notebookId as string
const noteId = route.params.noteId as string
const title = ref('')
const isLoading = ref(true)
const saveTimer = ref<ReturnType<typeof setTimeout> | null>(null)

const editor = useEditor({
  extensions: [
    StarterKit.configure({
      heading: { levels: [1, 2, 3] },
    }),
    Placeholder.configure({ placeholder: 'Start writing...' }),
    Highlight,
    TaskList,
    TaskItem.configure({ nested: true }),
    Table.configure({ resizable: true }),
    TableRow,
    TableCell,
    TableHeader,
    Link.configure({ openOnClick: false }),
    Underline,
    Typography,
    CharacterCount,
  ],
  onUpdate: () => {
    editorStore.markDirty()
    scheduleAutoSave()
  },
  editorProps: {
    attributes: {
      class: 'prose prose-sm dark:prose-invert max-w-none focus:outline-none min-h-[60vh] px-8 py-6',
    },
  },
})

function scheduleAutoSave() {
  if (saveTimer.value) clearTimeout(saveTimer.value)
  saveTimer.value = setTimeout(() => saveNote(), 3000)
}

async function saveNote() {
  if (!editor.value) return
  editorStore.setSaving(true)
  try {
    const content = editor.value.getJSON()
    await notesStore.updateNote(noteId, {
      title: title.value,
      content,
    })
    editorStore.markClean()
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to save' })
  } finally {
    editorStore.setSaving(false)
  }
}

async function saveAndClose() {
  await saveNote()
  if (!editorStore.isDirty) {
    router.push({ name: 'notebook-detail', params: { id: notebookId } })
  }
}

// Load note
onMounted(async () => {
  try {
    const note = await notesStore.fetchNote(noteId)
    title.value = note.title
    editorStore.currentNoteId = noteId
    if (note.content && editor.value) {
      editor.value.commands.setContent(note.content)
    }
    editorStore.markClean()
  } catch {
    ui.addToast({ type: 'error', message: 'Note not found' })
    router.push({ name: 'notebook-detail', params: { id: notebookId } })
  } finally {
    isLoading.value = false
  }
})

// Keyboard shortcut: Cmd/Ctrl+S to save
function handleKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 's') {
    e.preventDefault()
    saveNote()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
  if (saveTimer.value) clearTimeout(saveTimer.value)
  // Save on unmount if dirty
  if (editorStore.isDirty) saveNote()
})

// Auto-save on title change
watch(title, () => {
  editorStore.markDirty()
  scheduleAutoSave()
})
</script>

<template>
  <div v-if="isLoading" class="flex items-center justify-center py-32">
    <span class="i-ph-circle-notch animate-spin w-8 h-8 text-brand-500" />
  </div>

  <div v-else class="max-w-4xl mx-auto">
    <!-- Toolbar -->
    <div class="flex items-center gap-1 mb-4 p-2 glass rounded-xl border border-gray-200/50 dark:border-gray-800/50 overflow-x-auto sticky top-16 z-10">
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Bold (Cmd+B)"
        @click="editor?.chain().focus().toggleBold().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('bold') }"
      >
        <span class="i-ph-text-bolder w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Italic (Cmd+I)"
        @click="editor?.chain().focus().toggleItalic().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('italic') }"
      >
        <span class="i-ph-text-italic w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Underline (Cmd+U)"
        @click="editor?.chain().focus().toggleUnderline().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('underline') }"
      >
        <span class="i-ph-text-underline w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Highlight"
        @click="editor?.chain().focus().toggleHighlight().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('highlight') }"
      >
        <span class="i-ph-text-highlight w-5 h-5" />
      </button>

      <div class="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-1" />

      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Heading 1"
        @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('heading', { level: 1 }) }"
      >
        <span class="text-sm font-bold">H1</span>
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Heading 2"
        @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('heading', { level: 2 }) }"
      >
        <span class="text-sm font-bold">H2</span>
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Heading 3"
        @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('heading', { level: 3 }) }"
      >
        <span class="text-sm font-bold">H3</span>
      </button>

      <div class="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-1" />

      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Bullet List"
        @click="editor?.chain().focus().toggleBulletList().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('bulletList') }"
      >
        <span class="i-ph-list-bullets w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Ordered List"
        @click="editor?.chain().focus().toggleOrderedList().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('orderedList') }"
      >
        <span class="i-ph-list-numbers w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Task List"
        @click="editor?.chain().focus().toggleTaskList().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('taskList') }"
      >
        <span class="i-ph-check-square w-5 h-5" />
      </button>

      <div class="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-1" />

      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Blockquote"
        @click="editor?.chain().focus().toggleBlockquote().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('blockquote') }"
      >
        <span class="i-ph-quotes w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Code Block"
        @click="editor?.chain().focus().toggleCodeBlock().run()"
        :class="{ 'bg-brand-100 dark:bg-brand-900/30 text-brand-600': editor?.isActive('codeBlock') }"
      >
        <span class="i-ph-code w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Horizontal Rule"
        @click="editor?.chain().focus().setHorizontalRule().run()"
      >
        <span class="i-ph-minus w-5 h-5" />
      </button>

      <div class="flex-1" />

      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Undo"
        @click="editor?.chain().focus().undo().run()"
      >
        <span class="i-ph-arrow-counter-clockwise w-5 h-5" />
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title="Redo"
        @click="editor?.chain().focus().redo().run()"
      >
        <span class="i-ph-arrow-clockwise w-5 h-5" />
      </button>
    </div>

    <!-- Title -->
    <input
      v-model="title"
      type="text"
      placeholder="Note title..."
      class="w-full text-3xl font-bold bg-transparent border-none outline-none placeholder:text-gray-300 dark:placeholder:text-gray-700 mb-4 px-8"
    />

    <!-- Editor -->
    <div class="glass-card overflow-hidden">
      <EditorContent :editor="editor" />
    </div>

    <!-- Status bar -->
    <div class="flex items-center justify-between mt-4 px-2 text-xs text-gray-400">
      <div class="flex items-center gap-3">
        <span v-if="editorStore.isSaving" class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-amber-400 pulse-dot" />
          Saving...
        </span>
        <span v-else-if="editorStore.isDirty" class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-amber-400" />
          Unsaved changes
        </span>
        <span v-else class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-400" />
          Saved
        </span>
      </div>
      <div class="flex items-center gap-4">
        <span>{{ editor?.storage.characterCount?.characters() || 0 }} chars</span>
        <span>{{ editor?.storage.characterCount?.words() || 0 }} words</span>
        <UiButton variant="ghost" size="sm" @click="saveAndClose">
          <span class="i-ph-check w-4 h-4" />
          Done
        </UiButton>
      </div>
    </div>
  </div>
</template>
