<template>
  <main>
    <div class="archive">
      <div class="actions-container position-absolute top-0 right-0 m-5">
        <button
          class="btn btn-outline-primary my-4 me-2"
          @click="backToExhibition"
          aria-label="Zurück zur Ausstellung"
          title="Zurück zur Ausstellung"
        >
          <i-mdi-arrow-left-bold class="icon" />
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

    return {
      imageService,
      similarImagesService,

      graphContainer,
      graph,
      initializedNodeIds,
      isZooming,

      imageId,
    };
  },
  async mounted() {
    this.loadGraph();

    this.initializeNode(this.imageId);

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
    async loadNeighbours(imageId: string, depth: number | null = 0) {
      if (depth === 2) {
        return;
      }
      depth = depth ?? 0;

      const neighbours = await this.similarImagesService.getSimilarImages(imageId);
      const { nodes, links } = this.graph.graphData();

      for (const neighbour of neighbours.images) {
        if (
          this.imageId !== neighbour.image_id &&
          !this.initializedNodeIds.find((nodeId) => nodeId === neighbour.image_id)
        ) {
          this.initializedNodeIds.push(neighbour.image_id);
          await this.initializeNode(neighbour.image_id, imageId);

          this.loadNeighboursFireAndForget(neighbour.image_id, depth + 1);
        }
        if (!links.find((link: any) => link.source === imageId && link.target === neighbour)) {
          await this.waitForNodeInit(neighbour.image_id);
          this.initializeLink(imageId, neighbour.image_id);
        }
      }

      this.zoomToFit();
    },
    loadNeighboursFireAndForget(imageId: string, depth: number | null = 0) {
      setTimeout(() => {
        this.loadNeighbours(imageId, depth).catch((error) => {
          console.error(error);
        });
      }, 125);
    },
    async waitForNodeInit(nodeId: string) {
      let counter = 0;
      return new Promise<void>((resolve) => {
        const interval = setInterval(() => {
          if (this.initializedNodeIds.find((id) => id === nodeId)) {
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
    async initializeNode(imageId: string, sourceImageId?: string) {
      const imageUrl = this.imageService.getImageUrl(imageId, 256);
      const img = await this.loadImage(imageUrl);

      const node = { id: imageId, url: imageUrl, img: img };
      const link = { source: sourceImageId, target: imageId };

      const { nodes, links } = this.graph.graphData();
      const newNodes = [...nodes, node];
      const newLinks = sourceImageId ? [...links, link] : [...links];

      this.graph.graphData({
        nodes: newNodes,
        links: newLinks,
      });
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
        .enableNodeDrag(false)
        .cooldownTicks(200)
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
    drawNode({ img, x, y }, ctx) {
      const size = 16;
      ctx.drawImage(img, x - size / 2, y - size / 2, size, size);
    },
    drawPointerArea({ img, x, y }, color, ctx) {
      const size = 16;
      //ctx.drawImage(img, x - size / 2, y - size / 2, size, size);
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
