<!-- pages/index.vue -->
<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800">
    <div class="container mx-auto px-4 py-16">
      <!-- Header Section -->
      <div class="text-center mb-16">
        <h1 class="text-4xl font-bold text-white mb-4">
          Semantic Search Engine
        </h1>
        <p class="text-xl text-slate-300">
          Discover insights across patents and research papers
        </p>
      </div>

      <!-- Navigation Options -->
      <div class="max-w-3xl mx-auto grid md:grid-cols-2 gap-6">
        <NuxtLink
          to="/patents"
          class="p-6 rounded-lg border-2 border-slate-700 hover:border-blue-500 bg-slate-800/50 hover:bg-blue-500/10 transition-all group"
        >
          <h2 class="text-2xl font-semibold mb-2 text-white">Patent Search</h2>
          <p class="text-slate-300 group-hover:text-white">
            Search through millions of patent abstracts using semantic
            understanding
          </p>
        </NuxtLink>

        <NuxtLink
          to="/papers"
          class="p-6 rounded-lg border-2 border-slate-700 hover:border-blue-500 bg-slate-800/50 hover:bg-blue-500/10 transition-all group"
        >
          <h2 class="text-2xl font-semibold mb-2 text-white">Paper Search</h2>
          <p class="text-slate-300 group-hover:text-white">
            Explore academic papers and research using semantic search
          </p>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
