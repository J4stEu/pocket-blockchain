import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";
import svgLoader from "vite-svg-loader";
import AutoImport from "unplugin-auto-import/vite";
import Components from "unplugin-vue-components/vite";
import { ElementPlusResolver } from "unplugin-vue-components/resolvers";

// https://vitejs.dev/config/
export default defineConfig({
    resolve:{
        alias:{
            "@" : path.resolve(__dirname, "./src")
        },
    },
    css: {
        preprocessorOptions: {
            scss: {
                additionalData: "@import \"./src/assets/styles/variables.scss\";",
                // imports: [path.resolve(__dirname, "./src/assets/styles/main.scss")]
            },
        },
    },
    plugins: [
        vue(),
        svgLoader({defaultImport: "raw"}),
        AutoImport({
            resolvers: [ElementPlusResolver()],
        }),
        Components({
            resolvers: [ElementPlusResolver()],
        }),
    ],
    server: {
        proxy: {
            "/api": {
                target: "http://192.168.31.144:5000",
                changeOrigin: true,
                secure: false,
                rewrite: (path) => path.replace(/^\/api/, ""),
            }
        }
    }
});
