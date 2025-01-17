<template>
  <div class="mx-auto p-4 max-w-6xl">
    <h1 class="text-2xl font-bold mb-6">Patent Abstract Search</h1>

    <!-- Search Interface -->
    <div class="mb-6 space-y-4">
      <!-- Main Search -->
      <div class="flex gap-2">
        <input
          v-model="searchParams.q"
          placeholder="Search patent abstracts..."
          class="flex-1 p-3 border rounded text-lg"
          @keyup.enter="search"
        />
        <button
          @click="search"
          class="px-6 py-3 bg-blue-500 text-white rounded hover:bg-blue-600 text-lg"
          :disabled="isLoading"
        >
          {{ isLoading ? "Searching..." : "Search" }}
        </button>
      </div>

      <!-- Number of Results -->
      <div class="flex gap-4 p-4 bg-gray-50 rounded">
        <div class="space-y-2">
          <label class="block text-sm font-medium">Number of Results</label>
          <input
            v-model="searchParams.limit"
            type="number"
            min="1"
            max="100"
            class="w-24 p-2 border rounded"
          />
        </div>
      </div>
    </div>

    <!-- Results Stats -->
    <div v-if="results.length" class="mb-4 text-sm text-gray-600">
      Found {{ results.length }} results ({{ searchTime }}ms)
    </div>

    <!-- Search History -->
    <div v-if="searchHistory.length" class="mb-6">
      <h3 class="text-sm font-medium mb-2">Recent Searches:</h3>
      <div class="flex gap-2 flex-wrap">
        <button
          v-for="(search, index) in searchHistory"
          :key="index"
          @click="
            searchParams.q = search;
            search();
          "
          class="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
        >
          {{ search }}
        </button>
      </div>
    </div>

    <!-- Results -->
    <div v-if="results.length" class="space-y-6">
      <div
        v-for="result in results"
        :key="result.id"
        class="p-4 border rounded-lg hover:bg-gray-50"
      >
        <div class="flex justify-between items-start mb-2">
          <div class="flex items-center gap-2">
            <h2 class="text-lg font-semibold">
              Patent ID: {{ result.patentID }}
            </h2>
            <button
              @click="copyToClipboard(result.patentID)"
              class="p-1 text-gray-500 hover:text-gray-700 relative group flex flex-col items-center"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path
                  d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
                ></path>
              </svg>
              <span
                class="absolute top-7 rounded-lg z-10 text-xs hidden group-hover:block bg-gray-200 shadow-lg p-2 text-nowrap"
                >Copy Patent ID</span
              >
            </button>
          </div>
          <div class="text-sm font-medium" :class="getScoreClass(result.score)">
            Similarity: {{ (result.score * 100).toFixed(1) }}%
          </div>
        </div>

        <!-- Abstract with highlighted terms -->
        <!-- <p
            class="text-gray-700"
            v-html="highlightTerms(result.abstract, searchParams.q)"
          ></p> -->
      </div>
    </div>

    <!-- No Results -->
    <div
      v-else-if="!isLoading && searchParams.q"
      class="text-center text-gray-500 p-8"
    >
      No matching patents found
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";

const searchParams = reactive({
  q: "",
  limit: 10,
});

const results = ref([]);
const isLoading = ref(false);
const error = ref("");
const searchTime = ref(0);
const searchHistory = ref([]);

const search = async () => {
  if (!searchParams.q.trim()) return;

  try {
    isLoading.value = true;
    error.value = "";
    const startTime = performance.now();

    results.value = await $fetch("/api/search_patents", {
      params: searchParams,
    });

    searchTime.value = Math.round(performance.now() - startTime);

    // Add to search history
    if (!searchHistory.value.includes(searchParams.q)) {
      searchHistory.value.unshift(searchParams.q);
      searchHistory.value = searchHistory.value.slice(0, 5); // Keep last 5 searches
    }
  } catch (err) {
    error.value = "Failed to perform search. Please try again.";
    results.value = [];
  } finally {
    isLoading.value = false;
  }
};

const getScoreClass = (score) => {
  if (score >= 0.8) return "text-green-600";
  if (score >= 0.6) return "text-yellow-600";
  return "text-red-600";
};

const highlightTerms = (text, query) => {
  if (!query) return text;
  const terms = query.split(" ").filter((t) => t.length > 2);
  let highlighted = text;
  terms.forEach((term) => {
    const regex = new RegExp(term, "gi");
    highlighted = highlighted.replace(
      regex,
      (match) => `<span class="bg-yellow-100">${match}</span>`
    );
  });
  return highlighted;
};

const copyToClipboard = async (text) => {
  await navigator.clipboard.writeText(text);
};
</script>
