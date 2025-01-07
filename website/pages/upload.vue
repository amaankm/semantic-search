<template>
  <div class="max-w-2xl mx-auto p-4">
    <form @submit.prevent="uploadData" class="space-y-4">
      <div>
        <input
          v-model="metadata.title"
          placeholder="Enter title"
          class="w-full p-2 border rounded"
          required
        />
      </div>
      <div>
        <textarea
          v-model="text"
          placeholder="Enter text to index"
          class="w-full h-32 p-2 border rounded"
          required
        ></textarea>
      </div>
      <button
        type="submit"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        :disabled="isLoading"
      >
        {{ isLoading ? "Uploading..." : "Upload" }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";

const text = ref("");
const metadata = ref({ title: "" });
const isLoading = ref(false);

const uploadData = async () => {
  if (!text.value.trim() || !metadata.value.title.trim()) return;

  try {
    isLoading.value = true;
    await $fetch("/api/upload", {
      method: "POST",
      body: {
        text: text.value,
        metadata: {
          ...metadata.value,
          id: Date.now().toString(),
        },
      },
    });
    text.value = "";
    metadata.value.title = "";
    alert("Data uploaded successfully!");
  } catch (error) {
    alert("Failed to upload data. Please try again.");
  } finally {
    isLoading.value = false;
  }
};
</script>
