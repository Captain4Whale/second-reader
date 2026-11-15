/* Shared prefix-preserving JSONL write primitive for all annotator modes. */
(function (root) {
  function sorted(v) {
    return Array.isArray(v)
      ? v.map(sorted)
      : v && typeof v === "object"
        ? Object.fromEntries(
            Object.keys(v)
              .sort()
              .map((k) => [k, sorted(v[k])]),
          )
        : v;
  }
  function compare(local, remote) {
    for (let i = 0; i < Math.min(local.length, remote.length); i++)
      if (
        JSON.stringify(sorted(local[i])) !== JSON.stringify(sorted(remote[i]))
      )
        throw Error(
          "浏览器与文件历史发生分叉，已停止同步并保留双方内容；请导出浏览器记录后核对。",
        );
    return remote.length - local.length;
  }
  async function append(handle, rows, parse) {
    const journal = await (await handle.getFile()).text(),
      remote = parse(journal);
    if (compare(rows, remote) > 0)
      throw Error("文件有较新记录，已暂停写入；请重新连接核对并恢复。");
    const suffix = rows
      .slice(remote.length)
      .map((r) => JSON.stringify(r) + "\n")
      .join("");
    if (suffix) {
      const stream = await handle.createWritable({
        keepExistingData: true,
        mode: "exclusive",
      });
      try {
        const current = await handle.getFile();
        if ((await current.text()) !== journal)
          throw Error("结果文件已被其他窗口修改，请重试同步。");
        await stream.seek(current.size);
        await stream.write(suffix);
        await stream.close();
      } catch (e) {
        await stream.abort().catch(() => {});
        throw e;
      }
    }
    return rows.length;
  }
  root.Q1Journal = { compare, append };
  if (typeof module !== "undefined") module.exports = root.Q1Journal;
})(globalThis);
