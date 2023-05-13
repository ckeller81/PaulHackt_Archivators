<template>
  <main>
    <div class="archive">
      <div class="actions-container position-absolute top-0 right-0 m-5">
        <button
          v-if="!isLoadAll"
          class="btn btn-outline-primary my-4 me-2"
          @click="startLoadAll"
          aria-label="Alles anzeigen"
          title="Alles anzeigen"
        >
          <i-mdi-arrow-expand-all class="icon" />
        </button>
        <button
          v-else
          class="btn btn-outline-primary my-4 me-2"
          @click="stopLoadAll"
          aria-label="Laden abbrechen"
          title="Laden abbrechen"
        >
          <i-mdi-stop-remove class="icon text-danger" />
        </button>
      </div>
      <div ref="graphContainer" class="graph-container z-0" />
    </div>
  </main>
</template>

<script lang="ts">
import { ImageService } from "@/services/image-service";
import { SimilarImagesService } from "@/services/similar-images-service";
import ForceGraph from "force-graph";
import { ref } from "vue";
import { useRoute } from "vue-router";

export default {
  setup() {
    const router = useRoute();

    const imageService = new ImageService();
    const similarImagesService = new SimilarImagesService();

    const imageId = router.query.imageid as string; // Access the query parameter

    const graphContainer = ref<any>(null);
    const graph = ref<any>(null);
    const initializedNodeIds = ref<string[]>([]);
    const isZooming = ref(false);
    const loadNeighboursIsCancelled = ref(false);
    const isLoadAll = ref(false);
    const isPaning = ref(false);
    const parallelLoadingCount = ref(0);

    return {
      imageService,
      similarImagesService,

      graphContainer,
      graph,
      initializedNodeIds,
      isZooming,
      loadNeighboursIsCancelled,
      isLoadAll,
      isPaning,
      parallelLoadingCount,

      imageId,
    };
  },
  async mounted() {
    this.loadGraph();

    this.initializedNodeIds.push(this.imageId);
    this.initializeNode(this.imageId, undefined, true);

    this.zoomToFit();

    await this.loadNeighbours(this.imageId);
  },
  methods: {
    backToExhibition() {
      this.$router.push({
        name: "home",
        query: { imageid: this.imageId },
      });
    },
    async startLoadAll() {
      this.isLoadAll = true;
      this.loadNeighboursIsCancelled = false;

      this.loadGraph();
      this.initializedNodeIds = [];
      this.initializedNodeIds.push(this.imageId);
      this.initializeNode(this.imageId, undefined, true);

      this.zoomToFit();
      await this.loadNeighbours(this.imageId, 0, 50);
    },
    stopLoadAll() {
      this.isLoadAll = false;
      this.loadNeighboursIsCancelled = true;
    },
    async loadNeighbours(imageId: string, depth: number | null = 0, maxDepth: number = 3) {
      if (depth === maxDepth) {
        return;
      }
      depth = depth ?? 0;

      const neighbours = await this.similarImagesService.getSimilarImages(imageId);
      const { links } = this.graph.graphData();

      for (const neighbour of neighbours.images) {
        if (this.loadNeighboursIsCancelled) {
          return;
        }

        if (
          this.imageId !== neighbour.image_id &&
          !this.initializedNodeIds.find((nodeId) => nodeId === neighbour.image_id)
        ) {
          this.initializedNodeIds.push(neighbour.image_id);
          await this.initializeNode(neighbour.image_id, imageId);

          this.loadNeighboursFireAndForget(neighbour.image_id, depth + 1, maxDepth);
        }
        if (!links.find((link: any) => link.source === imageId && link.target === neighbour)) {
          await this.waitForNodeInit(neighbour.image_id);
          this.initializeLink(imageId, neighbour.image_id);
        }
      }

      this.zoomToFit();
    },
    loadNeighboursFireAndForget(imageId: string, depth: number | null = 0, maxDepth: number = 3) {
      if (this.loadNeighboursIsCancelled) {
        return;
      }

      setTimeout(() => {
        this.loadNeighbours(imageId, depth, maxDepth).catch((error) => {
          console.error(error);
        });
      }, 125);
    },
    async waitForNodeInit(nodeId: string) {
      let counter = 0;
      return new Promise<void>((resolve) => {
        const interval = setInterval(() => {
          const { nodes, links } = this.graph.graphData();
          if (
            this.initializedNodeIds.find((id) => id === nodeId) &&
            nodes.find((node: any) => node.id === nodeId)
          ) {
            clearInterval(interval);
            resolve();
          } else {
            counter++;
            if (counter > 100) {
              clearInterval(interval);
              resolve();
            }
          }
        }, 100);
      });
    },
    async initializeNode(imageId: string, sourceImageId?: string, isRootNode: boolean = false) {
      if (this.parallelLoadingCount > 10) {
        await new Promise((resolve) => setTimeout(resolve, 250));
      }
      this.parallelLoadingCount++;

      const imageUrl = this.imageService.getImageUrl(imageId, 512);
      const img = await this.loadImage(imageUrl);

      const node = { id: imageId, url: imageUrl, img: img, isRootNode: isRootNode };
      const link = { source: sourceImageId, target: imageId };

      const { nodes, links } = this.graph.graphData();
      const newNodes = [...nodes, node];
      const newLinks = sourceImageId ? [...links, link] : [...links];

      this.graph.graphData({
        nodes: newNodes,
        links: newLinks,
      });

      this.parallelLoadingCount--;
    },
    initializeLink(sourceImageId: string, targetImageId: string) {
      const link = { source: sourceImageId, target: targetImageId };

      const { nodes, links } = this.graph.graphData();
      const newLinks = [...links, link];

      this.graph.graphData({
        nodes: nodes,
        links: newLinks,
      });
    },
    async loadGraph() {
      this.graph = ForceGraph()(this.graphContainer);

      const data = {
        nodes: [],
        links: [],
      };

      const containerWidth = this.graphContainer.offsetWidth;
      const containerHeight = this.graphContainer.offsetHeight;

      this.graph
        .nodeCanvasObject(this.drawNode)
        .nodePointerAreaPaint(this.drawPointerArea)
        .width(containerWidth)
        .height(containerHeight)
        .cooldownTicks(200)
        .enableNodeDrag(false)
        .onZoom(() => {
          this.isPaning = true;
        })
        .onZoomEnd(() => {
          this.isPaning = false;
        })
        .onNodeClick((node, event) => {
          if (!this.isPaning) {
            this.$router.push({
              name: "home",
              query: { imageid: node.id },
            });
          }
        })
        .graphData(data);

      this.graph.onEngineStop(() => this.graph.zoomToFit(250, 50));
    },
    zoomToFit() {
      if (this.isZooming) {
        return;
      }

      this.isZooming = true;

      this.graph.zoomToFit(500, 50);
      setTimeout(() => {
        this.isZooming = false;
      }, 125);
    },
    drawNode(node, ctx) {
      const size = 16;
      ctx.drawImage(node.img, node.x - size / 2, node.y - size / 2, size, size);

      if (node.isRootNode) {
        ctx.lineWidth = 0.5;
        ctx.strokeStyle = "#ea583d";
        ctx.beginPath();
        ctx.rect(node.x - size / 2, node.y - size / 2, size, size);
        ctx.stroke();
      }
    },
    drawPointerArea(node, color, ctx) {
      const size = 16;
      ctx.fillStyle = color;
      ctx.fillRect(node.x - size / 2, node.y - size / 2, size, size); // draw square as pointer trap
    },
    loadImage(imageUrl: string) {
      const img = new Image();
      img.src = imageUrl;

      return new Promise((resolve) => {
        img.onload = () => {
          resolve(img);
        };
      });
    },
  },
};
</script>

<style lang="scss">
.archive {
  width: 100%;
  height: 100%;
  position: relative;

  .actions-container {
    z-index: 1;
  }

  .graph-container {
    z-index: 0;

    width: 100%;
    height: calc(100vh - 151px);
  }
}
</style>
