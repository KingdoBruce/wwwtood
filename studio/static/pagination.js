(() => {
  const POST_PAGE_SIZE = 10;
  const TAG_PAGE_SIZE = 12;
  let postPage = 1;
  let tagPage = 1;

  function normalizedSearchText(value) {
    return String(value || "")
      .normalize("NFKC")
      .toLocaleLowerCase()
      .replace(/[\s\-_:：，。、“”"'‘’【】\[\]（）()《》<>]+/g, "");
  }

  function fuzzyTitleMatch(title, query) {
    const target = normalizedSearchText(title);
    const needle = normalizedSearchText(query);
    if (!needle || target.includes(needle)) return true;
    let queryIndex = 0;
    for (const character of target) {
      if (character === needle[queryIndex]) queryIndex += 1;
      if (queryIndex === needle.length) return true;
    }
    return false;
  }

  async function loadChangeDetails() {
    const result = await api("/api/status");
    const list = document.getElementById("changeList");
    const items = result.change_items || [];
    list.innerHTML = items.map(item => `
      <div class="change-row">
        <div>
          <strong>${escapeHtml(item.title)}</strong>
          <small>${escapeHtml(item.path)}</small>
        </div>
        <span class="badge${item.draft ? " draft" : ""}">${escapeHtml(item.kind === "post" ? (item.draft ? "草稿文章" : "文章文件") : "程序文件")} · ${escapeHtml(item.state)}</span>
        ${item.kind === "post" ? `<div class="change-actions">
          <button type="button" class="text-button edit-change-post" data-slug="${escapeHtml(item.slug)}">编辑</button>
          <button type="button" class="text-button delete-change-post" data-slug="${escapeHtml(item.slug)}" data-title="${escapeHtml(item.title)}">移入回收站</button>
        </div>` : ""}
      </div>
    `).join("") || '<div class="empty">当前没有未发布的网站内容改动</div>';

    list.querySelectorAll(".edit-change-post").forEach(button => {
      button.onclick = () => editPost(button.dataset.slug);
    });
    list.querySelectorAll(".delete-change-post").forEach(button => {
      button.onclick = async () => {
        await deletePostBySlug(button.dataset.slug, button.dataset.title);
        await loadDashboard();
      };
    });
  }

  async function toggleChangeDetails(forceOpen) {
    const panel = document.getElementById("changeDetails");
    const button = document.getElementById("changeMetric");
    const open = forceOpen ?? panel.hidden;
    panel.hidden = !open;
    button.setAttribute("aria-expanded", String(open));
    if (open) {
      try {
        await loadChangeDetails();
      } catch (error) {
        notice(error.message, true);
      }
    }
  }

  document.getElementById("changeMetric").onclick = () => toggleChangeDetails();
  document.getElementById("closeChangeDetails").onclick = () => toggleChangeDetails(false);

  function paginationMarkup(page, totalPages, totalItems, label) {
    if (totalPages <= 1) return "";
    return `<nav class="studio-pagination" aria-label="${label}">
      <button type="button" data-page="${page - 1}" ${page <= 1 ? "disabled" : ""}><span>←</span><b>上一页</b></button>
      <span><small>PAGE</small><strong>${String(page).padStart(2, "0")} / ${String(totalPages).padStart(2, "0")}</strong><em>共 ${totalItems} 条</em></span>
      <button type="button" data-page="${page + 1}" ${page >= totalPages ? "disabled" : ""}><b>下一页</b><span>→</span></button>
    </nav>`;
  }

  function bindPagination(container, onChange) {
    container.querySelectorAll("button[data-page]").forEach(button => {
      button.onclick = () => {
        onChange(Number(button.dataset.page));
        const view = container.closest(".view");
        window.scrollTo({ top: Math.max(0, view.offsetTop - 20), behavior: "smooth" });
      };
    });
  }

  function renderPostPage() {
    const searchInput = document.getElementById("postSearch");
    const searchMeta = document.getElementById("postSearchMeta");
    const query = searchInput.value.trim().toLowerCase();
    const category = document.getElementById("postCategoryFilter").value;
    const filterEl = document.getElementById("postCategoryFilter");
    const currentFilter = filterEl.value;
    const categories = Array.from(new Set(posts.flatMap(post => post.categories || []))).sort((a, b) => a.localeCompare(b, "zh"));
    filterEl.innerHTML = `<option value="">全部分类</option>` + categories.map(name => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join("");
    filterEl.value = currentFilter;
    const batchEl = document.getElementById("postBatchCategory");
    const currentBatch = batchEl.value;
    batchEl.innerHTML = `<option value="">清除分类</option>` + categories.map(name => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join("");
    batchEl.value = currentBatch;
    const visiblePosts = posts.filter(post => {
      const matchesSearch = !query || [post.title, (post.categories || []).join(" "), (post.tags || []).join(" ")].join(" ").toLowerCase().includes(query);
      const matchesCategory = !category || (post.categories || []).includes(category);
      return matchesSearch && matchesCategory;
    });
    const totalPages = Math.max(1, Math.ceil(visiblePosts.length / POST_PAGE_SIZE));
    postPage = Math.min(Math.max(1, postPage), totalPages);
    const start = (postPage - 1) * POST_PAGE_SIZE;
    const pagePosts = visiblePosts.slice(start, start + POST_PAGE_SIZE);
    document.getElementById("postList").innerHTML = pagePosts.map((post, index) => `
      <article class="post-row" data-slug="${escapeHtml(post.slug)}">
        <input type="checkbox" class="post-check" data-slug="${escapeHtml(post.slug)}" title="选择此文章">
        <code>A.${String(visiblePosts.length - start - index).padStart(3, "0")}</code>
        <div>
          <strong>${escapeHtml(post.title)}</strong>
          <p>${escapeHtml(post.description || post.slug)}</p>
        </div>
        <span>${escapeHtml((post.categories || []).join(" / ") || "未分类")}</span>
        <time>${escapeHtml(fmtDate(post.date))}</time>
        <button type="button" class="text-button delete-post-row" data-slug="${escapeHtml(post.slug)}" data-title="${escapeHtml(post.title)}">删除</button>
      </article>
    `).join("") || (query || category
      ? '<div class="empty">没有找到匹配的文章</div>'
      : '<div class="empty">点击“新建文章”开始写作</div>');

    const pagination = document.getElementById("postPagination");
    pagination.innerHTML = paginationMarkup(postPage, totalPages, visiblePosts.length, query || category ? "文章筛选结果分页" : "文章管理分页");
    searchMeta.textContent = query || category ? `匹配 ${visiblePosts.length}/${posts.length} 篇` : "输入标题、分类或标签关键词";
    bindPagination(pagination, page => {
      postPage = page;
      renderPostPage();
    });

    document.querySelectorAll(".post-row").forEach(row => {
      row.onclick = event => {
        if (event.target.closest(".delete-post-row")) return;
        if (event.target.closest(".post-check")) {
          updatePostBatchState();
          return;
        }
        editPost(row.dataset.slug);
      };
    });
    document.querySelectorAll(".delete-post-row").forEach(button => {
      button.onclick = event => {
        event.stopPropagation();
        deletePostBySlug(button.dataset.slug, button.dataset.title);
      };
    });
    document.querySelectorAll(".post-check").forEach(input => {
      input.onchange = updatePostBatchState;
    });
    updatePostBatchState();
  }

  document.getElementById("postSearch").oninput = () => {
    postPage = 1;
    renderPostPage();
  };

  document.getElementById("postCategoryFilter").onchange = () => {
    postPage = 1;
    renderPostPage();
  };

  loadPosts = async function () {
    try {
      posts = (await api("/api/posts")).posts;
      renderPostPage();
    } catch (error) {
      notice(error.message, true);
    }
  };

  renderTaxonomy = function (kind) {
    const singular = kind === "categories" ? "分类" : "标签";
    const list = document.getElementById(kind === "categories" ? "categoryList" : "tagList");
    const total = document.getElementById(kind === "categories" ? "categoryTotal" : "tagTotal");
    const items = taxonomyData[kind] || [];
    let visibleItems = items;

    if (kind === "tags") {
      const totalPages = Math.max(1, Math.ceil(items.length / TAG_PAGE_SIZE));
      tagPage = Math.min(Math.max(1, tagPage), totalPages);
      const start = (tagPage - 1) * TAG_PAGE_SIZE;
      visibleItems = items.slice(start, start + TAG_PAGE_SIZE);
      const pagination = document.getElementById("tagPagination");
      pagination.innerHTML = paginationMarkup(tagPage, totalPages, items.length, "标签管理分页");
      bindPagination(pagination, page => {
        tagPage = page;
        renderTaxonomy("tags");
      });
    }

    total.textContent = items.length;
    list.innerHTML = visibleItems.map(item => `
      <div class="taxonomy-row${kind === "categories" ? " has-visibility" : ""}">
        <strong>${escapeHtml(item.name)}</strong>
        <small>${item.count} 篇文章</small>
        ${kind === "categories" ? `<div class="taxonomy-visibility">
          <label><span>首页显示</span><input class="category-display-toggle" type="checkbox" data-name="${encodeURIComponent(item.name)}" data-field="show_on_home" ${item.show_on_home !== false ? "checked" : ""}></label>
          <label><span>归档分类索引</span><input class="category-display-toggle" type="checkbox" data-name="${encodeURIComponent(item.name)}" data-field="show_in_archives" ${item.show_in_archives !== false ? "checked" : ""}></label>
        </div>` : ""}
        <div class="taxonomy-actions">
          <button class="button ghost rename-taxonomy" data-kind="${kind}" data-name="${encodeURIComponent(item.name)}">重命名</button>
          <button class="button ghost delete-taxonomy" data-kind="${kind}" data-name="${encodeURIComponent(item.name)}">删除</button>
        </div>
      </div>
    `).join("") || `<div class="empty">还没有${singular}</div>`;

    list.querySelectorAll(".category-display-toggle").forEach(input => {
      input.onchange = () => saveCategoryDisplay(input);
    });
    list.querySelectorAll(".rename-taxonomy").forEach(button => {
      button.onclick = () => renameTaxonomy(button.dataset.kind, decodeURIComponent(button.dataset.name));
    });
    list.querySelectorAll(".delete-taxonomy").forEach(button => {
      button.onclick = () => deleteTaxonomy(button.dataset.kind, decodeURIComponent(button.dataset.name));
    });
  };
})();
