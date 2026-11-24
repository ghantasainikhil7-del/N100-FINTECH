import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// Vite plugin to serve the publication-grade PDF reports directly from /reports folder
const serveReportsPlugin = () => ({
  name: 'serve-reports',
  configureServer(server) {
    server.middlewares.use((req, res, next) => {
      const url = req.url ? req.url.split('?')[0] : ''
      if (url.startsWith('/reports/') || url.startsWith('/api/v1/reports/')) {
        let relPath = url.replace('/api/v1/reports/', '/').replace('/reports/', '/')
        
        // Handle /tearsheet/TCS or /tearsheet/ADANIPORTS
        if (relPath.startsWith('/tearsheet/') || relPath.startsWith('tearsheet/')) {
          const ticker = relPath.split('/').pop().replace('.pdf', '')
          relPath = `tearsheets/${ticker}_tearsheet.pdf`
        } 
        // Handle /sector/Financials
        else if (relPath.startsWith('/sector/') || relPath.startsWith('sector/')) {
          const rawSec = decodeURIComponent(relPath.split('/').pop().replace('.pdf', ''))
          const sectorMap = {
            "Information Technology": "Information_Technology_report.pdf",
            "Financials": "Financials_report.pdf",
            "Energy": "Energy_report.pdf",
            "Healthcare": "Healthcare_report.pdf",
            "Materials": "Materials_report.pdf",
            "Consumer Discretionary": "Consumer_Discretionary_report.pdf",
            "Automobiles": "Consumer_Discretionary_report.pdf",
            "Consumer Staples": "Consumer_Staples_report.pdf",
            "Fast Moving Consumer Goods": "Consumer_Staples_report.pdf",
            "FMCG": "Consumer_Staples_report.pdf",
            "Industrials": "Industrials_report.pdf",
            "Communication Services": "Communication_Services_report.pdf",
            "Telecommunication": "Communication_Services_report.pdf",
            "Real Estate": "Real_Estate_report.pdf",
            "Conglomerates": "Energy_report.pdf",
          }
          const targetFile = sectorMap[rawSec] || `${rawSec.replace(/[^\w\-]/g, '_')}_report.pdf`
          relPath = `sector/${targetFile}`
        }

        const cleanRel = relPath.replace(/^\//, '')
        const filePath = path.resolve(__dirname, '..', 'reports', cleanRel)
        
        if (fs.existsSync(filePath)) {
          const filename = path.basename(filePath)
          res.setHeader('Content-Type', 'application/pdf')
          res.setHeader('Content-Disposition', `inline; filename="${filename}"`)
          return fs.createReadStream(filePath).pipe(res)
        }
      }
      next()
    })
  }
})

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), serveReportsPlugin()],
  css: {
    postcss: {
      plugins: []
    }
  },
  server: {
    port: 3000,
    open: true,
    hmr: {
      overlay: false
    }
  }
})
