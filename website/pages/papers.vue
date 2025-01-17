<template>
  <div class="max-w-6xl mx-auto p-4">
    <h1 class="text-2xl font-bold mb-6">Papers Abstract Search</h1>

    <!-- Search Interface -->
    <div class="mb-6 space-y-4">
      <!-- Main Search -->
      <div class="flex gap-2">
        <input
          v-model="searchParams.q"
          placeholder="Search paper abstracts..."
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
        <div class="space-y-2">
          <label class="block text-sm font-medium">Minimum Citations</label>
          <input
            v-model="searchParams.cited"
            type="number"
            min="1000"
            class="w-24 p-2 border rounded"
          />
        </div>
        <div class="space-y-2">
          <label class="block text-sm font-medium">From Year</label>
          <input
            v-model="searchParams.min_year"
            type="number"
            min="1763"
            class="w-24 p-2 border rounded"
          />
        </div>
        <div class="space-y-2">
          <label class="block text-sm font-medium">To Citations</label>
          <input
            v-model="searchParams.max_year"
            type="number"
            min="2025"
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
            <h2 class="text-xl font-bold">{{ result.title }}</h2>
            <NuxtLink
              :to="result.landing_page_url"
              target="_blank"
              class="p-1 text-gray-500 hover:text-gray-700 group flex flex-col items-center w-8 h-8"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                x="0px"
                y="0px"
                width="100"
                height="100"
                viewBox="0 0 48 48"
              >
                <path
                  d="M 41.470703 4.9863281 A 1.50015 1.50015 0 0 0 41.308594 5 L 27.5 5 A 1.50015 1.50015 0 1 0 27.5 8 L 37.878906 8 L 22.439453 23.439453 A 1.50015 1.50015 0 1 0 24.560547 25.560547 L 40 10.121094 L 40 20.5 A 1.50015 1.50015 0 1 0 43 20.5 L 43 6.6894531 A 1.50015 1.50015 0 0 0 41.470703 4.9863281 z M 12.5 8 C 8.3754991 8 5 11.375499 5 15.5 L 5 35.5 C 5 39.624501 8.3754991 43 12.5 43 L 32.5 43 C 36.624501 43 40 39.624501 40 35.5 L 40 25.5 A 1.50015 1.50015 0 1 0 37 25.5 L 37 35.5 C 37 38.003499 35.003499 40 32.5 40 L 12.5 40 C 9.9965009 40 8 38.003499 8 35.5 L 8 15.5 C 8 12.996501 9.9965009 11 12.5 11 L 22.5 11 A 1.50015 1.50015 0 1 0 22.5 8 L 12.5 8 z"
                ></path>
              </svg>
            </NuxtLink>
          </div>
          <div class="text-sm font-medium" :class="getScoreClass(result.score)">
            Similarity: {{ (result.score * 100).toFixed(1) }}%
          </div>
        </div>

        <div class="flex justify-between items-baseline gap-2 mb-2 text-nowrap">
          <h3 class="text-lg font-semibold">
            {{ result.host_organization_name }}, {{ result.publication_year }}
          </h3>
          <span>Cited : {{ result.cited_by_count }}</span>
        </div>

        <!-- Abstract with highlighted terms -->
        <p class="text-gray-700">{{ result.abstract }}</p>
      </div>
    </div>

    <!-- No Results -->
    <div
      v-else-if="!isLoading && searchParams.q"
      class="text-center text-gray-500 p-8"
    >
      No matching papers found
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";

const searchParams = reactive({
  q: "",
  limit: 10,
  cited: 1000,
  min_year: 1763,
  max_year: 2025,
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

    results.value = await $fetch("/api/search_papers", {
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
